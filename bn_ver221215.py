#####################################################################
# 모듈 설정
#####################################################################
import time
import telegram
import ccxt
import pprint
import pandas as pd

api_key = "1lAEsyiTW2QWiZrDgydSkCnUBpkFO5BHAlIW9VlbNJjLGjLGkGMp39wtO4X9iHAl"
secret  = "Ad9WCn91qPvNNJBeByW8HHZdBiBk1FaJsxDvPxoY2HZ4M2OI2FnQyIK55qQ6L3zB"

token = "5764591518:AAFX6_rSXGqTIowR8T0ezAH3ujFDCueVS8A"
id = "5457747234"
bot = telegram.Bot(token)

#binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}})

#btc 초기값
btc_long_loss_cut = 0
btc_short_loss_cut = 50000
btc_long_max_roe_01 = 0
btc_short_max_roe_01 = 0
btc_long_roe_01 = 0
btc_short_roe_01 = 0
btc_long_open_notice = 0
btc_short_open_notice = 0

#xrp 초기값
xrp_long_loss_cut = 0
xrp_short_loss_cut = 2
xrp_long_max_roe_01 = 0
xrp_short_max_roe_01 = 0
xrp_long_roe_01 = 0
xrp_short_roe_01 = 0
xrp_long_open_notice = 0
xrp_short_open_notice = 0

#doge 초기값
doge_long_loss_cut = 0
doge_short_loss_cut = 2
doge_long_max_roe_01 = 0
doge_short_max_roe_01 = 0
doge_long_roe_01 = 0
doge_short_roe_01 = 0
doge_long_open_notice = 0
doge_short_open_notice = 0

#eth 초기값
eth_long_loss_cut = 0
eth_short_loss_cut = 5000
eth_long_max_roe_01 = 0
eth_short_max_roe_01 = 0
eth_long_roe_01 = 0
eth_short_roe_01 = 0
eth_long_open_notice = 0
eth_short_open_notice = 0


class Mybinance():
    #생성자 (초기에 딱 한번 설정을 해주는 역할)
    def __init__(self):
        print("시작")
        
    def order(self, bal_symbol, order_symbol, btc_open_amt, btc_leverage):
        if(order_symbol == "BTC/USDT"):
            global btc_long_loss_cut
            global btc_short_loss_cut
            global btc_long_max_roe_01
            global btc_short_max_roe_01
            global btc_long_roe_01
            global btc_short_roe_01
            global btc_long_open_notice
            global btc_short_open_notice
            # 현재지갑 롱/숏 오픈상태 및 잔액
            balance = binance.fetch_balance(params = {"type" : "future"})
            positions = balance['info']['positions']
            for position in positions:
                if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                    btc_L_position = position
                elif position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                    btc_S_position = position
            btc_long_qty_01 = float(btc_L_position['positionAmt'])
            btc_short_qty_01 = float(btc_S_position['positionAmt'])
            btc_long_entryprice_01 = float(btc_L_position['entryPrice'])
            btc_short_entryprice_01 = float(btc_S_position['entryPrice'])

            markets = binance.load_markets()
            symbol = order_symbol
            market = binance.market(symbol)

            resp = binance.fapiPrivate_post_leverage({'symbol': market['id'],'leverage': btc_leverage})

            btc_1m = binance.fetch_ohlcv(symbol = symbol, timeframe = '1m', since = None, limit = 1201)
            btc_ticker_df_01 = pd.DataFrame(btc_1m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            btc_ticker_df_01['datetime'] = pd.to_datetime(btc_ticker_df_01['datetime'], unit='ms')
            btc_ticker_df_01.set_index('datetime', inplace=True)
            btc_15m = binance.fetch_ohlcv(symbol = symbol, timeframe = '15m', since = None, limit = 50)
            btc_ticker_df_02 = pd.DataFrame(btc_15m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            btc_ticker_df_02['datetime'] = pd.to_datetime(btc_ticker_df_02['datetime'], unit='ms')
            btc_ticker_df_02.set_index('datetime', inplace=True)
            # 단순이평선
            btc_ticker_df_01[ 'ma12'] = btc_ticker_df_01["close"].rolling(window=12).mean()
            btc_ticker_df_01[ 'ma20'] = btc_ticker_df_01["close"].rolling(window=20).mean()
            btc_ticker_df_01['ma120'] = btc_ticker_df_01["close"].rolling(window=120).mean()
            btc_ticker_df_01['ma1200'] = btc_ticker_df_01["close"].rolling(window=1200).mean()
            btc_ticker_df_02[ 'ma36'] = btc_ticker_df_02["close"].rolling(window=50).mean()
            # 지수이평선
            btc_ticker_df_01['ema3'] = btc_ticker_df_01['close'].ewm(span=3).mean()
            btc_ticker_df_01['ema2'] = btc_ticker_df_01['close'].ewm(span=2).mean()
            
            #볼린저밴드 구하기
            btc_ticker_df_01['std20'] = btc_ticker_df_01["close"].rolling(window=20).std()
            btc_ticker_df_01[ 'bu20'] = btc_ticker_df_01[ "ma20"] + btc_ticker_df_01['std20'] * 2
            btc_ticker_df_01[ 'bl20'] = btc_ticker_df_01[ "ma20"] - btc_ticker_df_01['std20'] * 2
            btc_ticker_df_01[ 'bm20'] = (btc_ticker_df_01[ 'bu20'] + btc_ticker_df_01[ 'bl20']) / 2

            btc_std20 = btc_ticker_df_01['std20'] = btc_ticker_df_01['close'].rolling(20).std()
            #btc_stdp = round((btc_std20[-1] / current_price * 100) ,2)
            btc_ticker_df_01['bbu'] = btc_ticker_df_01['ma20'] + btc_ticker_df_01['std20'] * 4
            btc_ticker_df_01['bbl'] = btc_ticker_df_01['ma20'] - btc_ticker_df_01['std20'] * 4

            # 숏 로스컷 : 돈치안20 최대최고
            btc_ticker_df_01[ 'max_high_20'] = btc_ticker_df_01['high'].rolling(20, axis = 0).max() 
            
            # 롱 로스컷 : 돈치안20 최소최저
            btc_ticker_df_01[  'min_low_20'] = btc_ticker_df_01[ 'low'].rolling(20, axis = 0).min()
            
            btc_ticker_df_01[   'middle_20'] = (btc_ticker_df_01['max_high_20'] + btc_ticker_df_01['min_low_20']) / 2

            btc_ticker_df_01.head() # 이거 왜하는지?
            btc_ticker_df_02.head()

            btc_current_price = btc_ticker_df_01['close'][-1]
                        
            if(btc_long_qty_01 > 0):
                btc_long_roe_01 = (btc_current_price - btc_long_entryprice_01) / btc_long_entryprice_01 * 100

            if(btc_long_roe_01 > btc_long_max_roe_01):
                btc_long_max_roe_01 = btc_long_roe_01
            
            if(btc_short_qty_01 < 0):
                btc_short_roe_01 = (btc_short_entryprice_01 - btc_current_price) / btc_short_entryprice_01 * 100
            
            if(btc_short_roe_01 > btc_short_max_roe_01):
                btc_short_max_roe_01 = btc_short_roe_01

            #지정가주문 실패시 시장가주문
            if(btc_long_qty_01 < btc_open_amt and btc_long_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'LONG'}
                data = binance.create_market_buy_order(order_symbol, btc_open_amt - btc_long_qty_01, params)            
                
            if(btc_long_qty_01 > 0 and btc_long_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                        btc_L_position = position
                btc_long_qty_01 = float(btc_L_position['positionAmt'])
                btc_long_entryprice_01 = float(btc_L_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="BTC Long Open" + "\n" + "entry price : " + str(btc_long_entryprice_01) + "\n" + "amount : " + str(btc_long_qty_01))
                btc_long_open_notice = 0
                
            #지정가주문 실패시 시장가주문
            if(btc_short_qty_01 > btc_open_amt * -1 and btc_short_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'SHORT'}
                data = binance.create_market_sell_order(order_symbol, btc_open_amt + btc_short_qty_01, params)  

            if(btc_short_qty_01 < 0 and btc_short_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                        btc_S_position = position
                btc_short_qty_01 = float(btc_S_position['positionAmt'])
                btc_short_entryprice_01 = float(btc_S_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="BTC Short Open" + "\n" + "entry price : " + str(btc_short_entryprice_01) + "\n" + "amount : " + str(btc_short_qty_01))
                btc_short_open_notice = 0

            # ###############################################################################################
            # Long. open
            ###############################################################################################
            if (btc_long_qty_01 == 0 and
                btc_ticker_df_01['ema2'][-2] < btc_ticker_df_01['ma1200'][-2] and
                btc_ticker_df_01['ema2'][-1] > btc_ticker_df_01['ma1200'][-1]):
                btc_long_loss_cut = btc_ticker_df_01[  'min_low_20'][-1]
                
                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, btc_open_amt, btc_current_price, params)
                btc_long_open_notice = 1

                if((btc_current_price - btc_long_loss_cut) / btc_current_price < 0.002):
                    btc_long_loss_cut = round(btc_current_price * 0.998,1)
            
            elif (btc_long_qty_01 == 0 and
                btc_ticker_df_01['ema2'][-2] > btc_ticker_df_01['ma1200'][-2] and
                btc_ticker_df_01['low'][-1] < btc_ticker_df_01['ma1200'][-1] and
                btc_current_price > btc_ticker_df_01['ma1200'][-1]):
                btc_long_loss_cut = btc_ticker_df_01[  'min_low_20'][-1]

                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, btc_open_amt, btc_current_price, params)
                btc_long_open_notice = 1

                if((btc_current_price - btc_long_loss_cut) / btc_current_price < 0.002):
                    btc_long_loss_cut = round(btc_current_price * 0.998,1)
            ###############################################################################################
            # Short. open
            ###############################################################################################
            if (btc_short_qty_01 == 0 and
                btc_ticker_df_01['ema2'][-2] > btc_ticker_df_01['ma1200'][-2] and
                btc_ticker_df_01['ema2'][-1] < btc_ticker_df_01['ma1200'][-1]):

                btc_short_loss_cut = btc_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, btc_open_amt, btc_current_price, params)
                btc_short_open_notice = 1

                if((btc_short_loss_cut - btc_current_price) / btc_current_price < 0.002):
                    btc_long_loss_cut = round(btc_current_price * 1.002,1)
            elif (btc_short_qty_01 == 0 and
                btc_ticker_df_01['ema2'][-1] < btc_ticker_df_01['ma1200'][-1] and
                btc_ticker_df_01['high'][-1] > btc_ticker_df_01['ma1200'][-2] and
                btc_current_price < btc_ticker_df_01['ma1200'][-1]):
                btc_short_loss_cut = btc_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, btc_open_amt, btc_current_price, params)
                btc_short_open_notice = 1
                
                if((btc_short_loss_cut - btc_current_price) / btc_current_price < 0.002):
                    btc_long_loss_cut = round(btc_current_price * 1.002,1)
            
            ###############################################################################################
            # Long. 손절
            ###############################################################################################
            if (btc_long_qty_01 > 0 and btc_ticker_df_01['close'][-1] < btc_long_loss_cut):
                bot.sendMessage(chat_id=id, text="Long lose cut" + "\n" + str(btc_long_roe_01) + "\n" + "amount : " + str(btc_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, btc_open_amt, params)
                btc_long_loss_cut = 0
                btc_long_roe_01 = 0
                btc_long_max_roe_01 = 0

            if (btc_long_qty_01 > 0 and btc_long_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="BTC Long lose cut" + "\n" + str(btc_long_roe_01) + "\n" + "amount : " + str(btc_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, btc_open_amt, params)
                btc_long_loss_cut = 0
                btc_long_roe_01 = 0
                btc_long_max_roe_01 = 0

            if (btc_long_qty_01 > 0 and btc_long_max_roe_01 > 0.55 and 
                btc_current_price <= btc_long_entryprice_01 and btc_current_price < btc_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="BTC Long 수익실현 후 lose cut" + "\n" + str(btc_long_roe_01) + "\n" + "amount : " + str(btc_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, btc_long_qty_01, params)
                btc_long_loss_cut = 0
                btc_long_roe_01 = 0
                btc_long_max_roe_01 = 0
              
            ###############################################################################################
            # Short. 손절
            ###############################################################################################
            if (btc_short_qty_01 < 0 and
                btc_ticker_df_01['close'][-1] > btc_short_loss_cut):
                bot.sendMessage(chat_id=id, text="BTC Short lose cut" + "\n" + str(btc_short_roe_01) + "\n" + "amount : " + str(btc_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, btc_open_amt, params)
                btc_short_loss_cut = 50000
                btc_short_roe_01 = 0
                btc_short_max_roe_01 = 0

            if (btc_short_qty_01 < 0 and btc_short_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="BTC Short lose cut" + "\n" + str(btc_short_roe_01) + "\n" + "amount : " + str(btc_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, btc_open_amt, params)

                btc_short_loss_cut = 50000
                btc_short_roe_01 = 0
                btc_short_max_roe_01 = 0

            if (btc_short_qty_01 < 0 and btc_short_max_roe_01 > 0.55 and 
                btc_current_price >= btc_short_entryprice_01 and btc_current_price > btc_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="BTC Short 수익실현 후 lose cut" + "\n" + str(btc_short_roe_01) + "\n" + "amount : " + str(btc_short_qty_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, btc_short_qty_01 * -1, params)
                btc_short_loss_cut = 50000
                btc_short_roe_01 = 0
                btc_short_max_roe_01 = 0       

            ###############################################################################################
            # Long. 수익실현
            ###############################################################################################
            if  (
                btc_long_qty_01 == btc_open_amt and
                btc_long_roe_01 > 0.5 and
                btc_ticker_df_01['ma12'][-1] > btc_ticker_df_01['ema2'][-1]
                ):
                params = {'positionSide' : 'LONG'}
                data = binance.create_limit_sell_order(order_symbol, btc_open_amt / 4, btc_current_price, params)
                bot.sendMessage(chat_id=id, text="BTC long profit 1st realize" + "\n" + "long max roe : " + str(btc_long_max_roe_01) + "\n" + "long roe : " + str(btc_long_roe_01))
            
            # elif  (btc_long_qty_01 == btc_open_amt and btc_long_max_roe_01 > 0.33 and btc_long_roe_01 <= 0.3):
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, btc_open_amt / 4, params)
            #     bot.sendMessage(chat_id=id, text="BTC long profit 1st realize" + "\n" + "long max roe : " + str(btc_long_max_roe_01) + "\n" + "long roe : " + str(btc_long_roe_01))

            elif (btc_long_qty_01 >= (btc_open_amt * 3) / 4 and btc_long_qty_01 < btc_open_amt and
                btc_long_roe_01 > 1 and
                btc_ticker_df_01['ma12'][-1] > btc_ticker_df_01['ema2'][-1]
                ):
                bot.sendMessage(chat_id=id, text="BTC long profit 2nd realize" + "\n" + "long max roe : " + str(btc_long_max_roe_01) + "\n" + "long roe : " + str(btc_long_roe_01))

                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, btc_open_amt / 4, params)

            # elif (btc_long_qty_01 >= (btc_open_amt * 3) / 4 and btc_long_qty_01 < btc_open_amt and
            #     btc_long_max_roe_01 > 0.63 and
            #     btc_long_roe_01 <= 0.6
            #     ):
            #     bot.sendMessage(chat_id=id, text="BTC long profit 2nd realize" + "\n" + "long max roe : " + str(btc_long_max_roe_01) + "\n" + "long roe : " + str(btc_long_roe_01))
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, btc_open_amt / 4, params)

            elif( btc_long_qty_01 > 0 and btc_long_max_roe_01 > 1
                and btc_long_roe_01 <= btc_long_max_roe_01 * 0.8
                and btc_ticker_df_01['ma12'][-1] > btc_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="BTC long profit final realize" + "\n" + "long max roe : " + str(btc_long_max_roe_01) + "\n" + "long roe : " + str(btc_long_roe_01))
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, btc_long_qty_01, params)

                btc_long_roe_01 = 0
                btc_long_max_roe_01 = 0

            ###############################################################################################
            # Short. 수익실현
            ###############################################################################################
            if  (btc_short_qty_01 == btc_open_amt * -1 and
                btc_short_roe_01 > 0.5 and
                btc_ticker_df_01[ 'ma12'][-1] < btc_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="BTC short profit 1st realize" + "\n" + "short max roe : " + str(btc_short_max_roe_01) + "\n" + "short roe : " + str(btc_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_limit_buy_order(order_symbol, btc_open_amt / 4, btc_current_price, params)

            # elif  (btc_short_qty_01 == btc_open_amt * -1 and
            #     btc_short_max_roe_01 > 0.33 and
            #     btc_short_roe_01 <= 0.3):
            #     bot.sendMessage(chat_id=id, text="BTC short profit 1st realize" + "\n" + "short max roe : " + str(btc_short_max_roe_01) + "\n" + "short roe : " + str(btc_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, btc_open_amt / 4, params)

            elif (btc_short_qty_01 <= ((btc_open_amt *3) / 4) * -1 and btc_short_qty_01 > btc_open_amt * -1 and
                btc_short_roe_01 > 1 and
                btc_ticker_df_01['ma12'][-1] < btc_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="BTC short profit 2nd realize" + "\n" + "short max roe : " + str(btc_short_max_roe_01) + "\n" + "short roe : " + str(btc_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, btc_open_amt / 4, params)

            # elif (btc_short_qty_01 <= ((btc_open_amt *3) / 4) * -1 and btc_short_qty_01 > btc_open_amt * -1 and
            #     btc_short_max_roe_01 > 0.63 and
            #     btc_short_roe_01 <= 0.60):
            #     bot.sendMessage(chat_id=id, text="BTC short profit 2nd realize" + "\n" + "short max roe : " + str(btc_short_max_roe_01) + "\n" + "short roe : " + str(btc_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, btc_open_amt / 4, params)
            
            elif( btc_short_qty_01 < 0 and btc_short_max_roe_01 > 1 and
                btc_short_roe_01 <= btc_short_max_roe_01 * 0.8 and
                btc_ticker_df_01['ma12'][-1] < btc_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="BTC short profit final realize" + "\n" + "short max roe : " + str(btc_short_max_roe_01) + "\n" + "short roe : " + str(btc_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, btc_short_qty_01 * -1, params)

                btc_short_roe_01 = 0
                btc_short_max_roe_01 = 0
        
            time.sleep(1)
            # 현재시간
            now = time.localtime()
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print(order_symbol)
            print("long amt      : ", btc_long_qty_01)
            print("long max roe  : ", btc_long_max_roe_01)
            print("long roe      : ", btc_long_roe_01)
            print("short amt     : ", btc_short_qty_01)
            print("short max roe : ", btc_short_max_roe_01)
            print("short roe     : ", btc_short_roe_01)
            print("current price : ", btc_current_price)
            print("1200ma        : ", round(btc_ticker_df_01['ma1200'][-1],1))
            print("==================================================")


   
    def order2(self, bal_symbol, order_symbol, xrp_open_amt, xrp_leverage):
        if(order_symbol == "XRP/USDT"):
            global xrp_long_loss_cut
            global xrp_short_loss_cut
            global xrp_long_max_roe_01
            global xrp_short_max_roe_01
            global xrp_long_roe_01
            global xrp_short_roe_01
            global xrp_long_open_notice
            global xrp_short_open_notice
            # 현재지갑 롱/숏 오픈상태 및 잔액
            balance = binance.fetch_balance(params = {"type" : "future"})
            positions = balance['info']['positions']
            for position in positions:
                if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                    xrp_L_position = position
                elif position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                    xrp_S_position = position
            xrp_long_qty_01 = float(xrp_L_position['positionAmt'])
            xrp_short_qty_01 = float(xrp_S_position['positionAmt'])
            xrp_long_entryprice_01 = float(xrp_L_position['entryPrice'])
            xrp_short_entryprice_01 = float(xrp_S_position['entryPrice'])

            markets = binance.load_markets()
            symbol = order_symbol
            market = binance.market(symbol)

            resp = binance.fapiPrivate_post_leverage({'symbol': market['id'],'leverage': xrp_leverage})

            xrp_1m = binance.fetch_ohlcv(symbol = symbol, timeframe = '1m', since = None, limit = 1201)
            xrp_ticker_df_01 = pd.DataFrame(xrp_1m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            xrp_ticker_df_01['datetime'] = pd.to_datetime(xrp_ticker_df_01['datetime'], unit='ms')
            xrp_ticker_df_01.set_index('datetime', inplace=True)
            xrp_15m = binance.fetch_ohlcv(symbol = symbol, timeframe = '15m', since = None, limit = 50)
            xrp_ticker_df_02 = pd.DataFrame(xrp_15m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            xrp_ticker_df_02['datetime'] = pd.to_datetime(xrp_ticker_df_02['datetime'], unit='ms')
            xrp_ticker_df_02.set_index('datetime', inplace=True)
            # 단순이평선
            xrp_ticker_df_01[ 'ma12'] = xrp_ticker_df_01["close"].rolling(window=12).mean()
            xrp_ticker_df_01[ 'ma20'] = xrp_ticker_df_01["close"].rolling(window=20).mean()
            xrp_ticker_df_01['ma120'] = xrp_ticker_df_01["close"].rolling(window=120).mean()
            xrp_ticker_df_01['ma1200'] = xrp_ticker_df_01["close"].rolling(window=1200).mean()
            xrp_ticker_df_02[ 'ma36'] = xrp_ticker_df_02["close"].rolling(window=50).mean()
            # 지수이평선
            xrp_ticker_df_01['ema3'] = xrp_ticker_df_01['close'].ewm(span=3).mean()
            xrp_ticker_df_01['ema2'] = xrp_ticker_df_01['close'].ewm(span=2).mean()
            
            #볼린저밴드 구하기
            xrp_ticker_df_01['std20'] = xrp_ticker_df_01["close"].rolling(window=20).std()
            xrp_ticker_df_01[ 'bu20'] = xrp_ticker_df_01[ "ma20"] + xrp_ticker_df_01['std20'] * 2
            xrp_ticker_df_01[ 'bl20'] = xrp_ticker_df_01[ "ma20"] - xrp_ticker_df_01['std20'] * 2
            xrp_ticker_df_01[ 'bm20'] = (xrp_ticker_df_01[ 'bu20'] + xrp_ticker_df_01[ 'bl20']) / 2

            xrp_std20 = xrp_ticker_df_01['std20'] = xrp_ticker_df_01['close'].rolling(20).std()
            #xrp_stdp = round((xrp_std20[-1] / current_price * 100) ,2)
            xrp_ticker_df_01['bbu'] = xrp_ticker_df_01['ma20'] + xrp_ticker_df_01['std20'] * 4
            xrp_ticker_df_01['bbl'] = xrp_ticker_df_01['ma20'] - xrp_ticker_df_01['std20'] * 4

            # 숏 로스컷 : 돈치안20 최대최고
            xrp_ticker_df_01[ 'max_high_20'] = xrp_ticker_df_01['high'].rolling(20, axis = 0).max() 
            
            # 롱 로스컷 : 돈치안20 최소최저
            xrp_ticker_df_01[  'min_low_20'] = xrp_ticker_df_01[ 'low'].rolling(20, axis = 0).min()
            
            xrp_ticker_df_01[   'middle_20'] = (xrp_ticker_df_01['max_high_20'] + xrp_ticker_df_01['min_low_20']) / 2

            xrp_ticker_df_01.head() # 이거 왜하는지?
            xrp_ticker_df_02.head()

            xrp_current_price = xrp_ticker_df_01['close'][-1]
                        
            if(xrp_long_qty_01 > 0):
                xrp_long_roe_01 = (xrp_current_price - xrp_long_entryprice_01) / xrp_long_entryprice_01 * 100

            if(xrp_long_roe_01 > xrp_long_max_roe_01):
                xrp_long_max_roe_01 = xrp_long_roe_01
            
            if(xrp_short_qty_01 < 0):
                xrp_short_roe_01 = (xrp_short_entryprice_01 - xrp_current_price) / xrp_short_entryprice_01 * 100
            
            if(xrp_short_roe_01 > xrp_short_max_roe_01):
                xrp_short_max_roe_01 = xrp_short_roe_01

            #지정가주문 실패시 시장가주문
            if(xrp_long_qty_01 < xrp_open_amt and xrp_long_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'LONG'}
                data = binance.create_market_buy_order(order_symbol, xrp_open_amt - xrp_long_qty_01, params)            
                
            if(xrp_long_qty_01 > 0 and xrp_long_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                        xrp_L_position = position
                xrp_long_qty_01 = float(xrp_L_position['positionAmt'])
                xrp_long_entryprice_01 = float(xrp_L_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="XRP Long Open" + "\n" + "entry price : " + str(xrp_long_entryprice_01) + "\n" + "amount : " + str(xrp_long_qty_01))
                xrp_long_open_notice = 0
                
            #지정가주문 실패시 시장가주문
            if(xrp_short_qty_01 > xrp_open_amt * -1 and xrp_short_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'SHORT'}
                data = binance.create_market_sell_order(order_symbol, xrp_open_amt + xrp_short_qty_01, params)  

            if(xrp_short_qty_01 < 0 and xrp_short_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                        xrp_S_position = position
                xrp_short_qty_01 = float(xrp_S_position['positionAmt'])
                xrp_short_entryprice_01 = float(xrp_S_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="XRP Short Open" + "\n" + "entry price : " + str(xrp_short_entryprice_01) + "\n" + "amount : " + str(xrp_short_qty_01))
                xrp_short_open_notice = 0

            # ###############################################################################################
            # Long. open
            ###############################################################################################
            if (xrp_long_qty_01 == 0 and
                xrp_ticker_df_01['ema2'][-2] < xrp_ticker_df_01['ma1200'][-2] and
                xrp_ticker_df_01['ema2'][-1] > xrp_ticker_df_01['ma1200'][-1]):
                xrp_long_loss_cut = xrp_ticker_df_01[  'min_low_20'][-1]
                
                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, xrp_open_amt, xrp_current_price, params)
                xrp_long_open_notice = 1

                if((xrp_current_price - xrp_long_loss_cut) / xrp_current_price < 0.002):
                    xrp_long_loss_cut = round(xrp_current_price * 0.998,4)
            
            elif (xrp_long_qty_01 == 0 and
                xrp_ticker_df_01['ema2'][-2] > xrp_ticker_df_01['ma1200'][-2] and
                xrp_ticker_df_01['low'][-1] < xrp_ticker_df_01['ma1200'][-1] and
                xrp_current_price > xrp_ticker_df_01['ma1200'][-1]):
                xrp_long_loss_cut = xrp_ticker_df_01[  'min_low_20'][-1]

                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, xrp_open_amt, xrp_current_price, params)
                xrp_long_open_notice = 1

                if((xrp_current_price - xrp_long_loss_cut) / xrp_current_price < 0.002):
                    xrp_long_loss_cut = round(xrp_current_price * 0.998,4)
            ###############################################################################################
            # Short. open
            ###############################################################################################
            if (xrp_short_qty_01 == 0 and
                xrp_ticker_df_01['ema2'][-2] > xrp_ticker_df_01['ma1200'][-2] and
                xrp_ticker_df_01['ema2'][-1] < xrp_ticker_df_01['ma1200'][-1]):

                xrp_short_loss_cut = xrp_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, xrp_open_amt, xrp_current_price, params)
                xrp_short_open_notice = 1

                if((xrp_short_loss_cut - xrp_current_price) / xrp_current_price < 0.002):
                    xrp_long_loss_cut = round(xrp_current_price * 1.002,4)
            elif (xrp_short_qty_01 == 0 and
                xrp_ticker_df_01['ema2'][-1] < xrp_ticker_df_01['ma1200'][-1] and
                xrp_ticker_df_01['high'][-1] > xrp_ticker_df_01['ma1200'][-2] and
                xrp_current_price < xrp_ticker_df_01['ma1200'][-1]):
                xrp_short_loss_cut = xrp_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, xrp_open_amt, xrp_current_price, params)
                xrp_short_open_notice = 1
                
                if((xrp_short_loss_cut - xrp_current_price) / xrp_current_price < 0.002):
                    xrp_long_loss_cut = round(xrp_current_price * 1.002,4)
            
            ###############################################################################################
            # Long. 손절
            ###############################################################################################
            if (xrp_long_qty_01 > 0 and xrp_ticker_df_01['close'][-1] < xrp_long_loss_cut):
                bot.sendMessage(chat_id=id, text="Long lose cut" + "\n" + str(xrp_long_roe_01) + "\n" + "amount : " + str(xrp_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, xrp_open_amt, params)
                xrp_long_loss_cut = 0
                xrp_long_roe_01 = 0
                xrp_long_max_roe_01 = 0

            if (xrp_long_qty_01 > 0 and xrp_long_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="XRP Long lose cut" + "\n" + str(xrp_long_roe_01) + "\n" + "amount : " + str(xrp_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, xrp_open_amt, params)
                xrp_long_loss_cut = 0
                xrp_long_roe_01 = 0
                xrp_long_max_roe_01 = 0

            if (xrp_long_qty_01 > 0 and xrp_long_max_roe_01 > 0.55 and 
                xrp_current_price <= xrp_long_entryprice_01 and xrp_current_price < xrp_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="XRP Long 수익실현 후 lose cut" + "\n" + str(xrp_long_roe_01) + "\n" + "amount : " + str(xrp_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, xrp_long_qty_01, params)
                xrp_long_loss_cut = 0
                xrp_long_roe_01 = 0
                xrp_long_max_roe_01 = 0
              
            ###############################################################################################
            # Short. 손절
            ###############################################################################################
            if (xrp_short_qty_01 < 0 and
                xrp_ticker_df_01['close'][-1] > xrp_short_loss_cut):
                bot.sendMessage(chat_id=id, text="XRP Short lose cut" + "\n" + str(xrp_short_roe_01) + "\n" + "amount : " + str(xrp_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, xrp_open_amt, params)
                xrp_short_loss_cut = 50000
                xrp_short_roe_01 = 0
                xrp_short_max_roe_01 = 0

            if (xrp_short_qty_01 < 0 and xrp_short_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="XRP Short lose cut" + "\n" + str(xrp_short_roe_01) + "\n" + "amount : " + str(xrp_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, xrp_open_amt, params)

                xrp_short_loss_cut = 50000
                xrp_short_roe_01 = 0
                xrp_short_max_roe_01 = 0

            if (xrp_short_qty_01 < 0 and xrp_short_max_roe_01 > 0.55 and 
                xrp_current_price >= xrp_short_entryprice_01 and xrp_current_price > xrp_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="XRP Short 수익실현 후 lose cut" + "\n" + str(xrp_short_roe_01) + "\n" + "amount : " + str(xrp_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, xrp_short_qty_01 * -1, params)
                xrp_short_loss_cut = 50000
                xrp_short_roe_01 = 0
                xrp_short_max_roe_01 = 0       

            ###############################################################################################
            # Long. 수익실현
            ###############################################################################################
            if  (
                xrp_long_qty_01 == xrp_open_amt and
                xrp_long_roe_01 > 0.5 and
                xrp_ticker_df_01['ma12'][-1] > xrp_ticker_df_01['ema2'][-1]
                ):
                params = {'positionSide' : 'LONG'}
                data = binance.create_limit_sell_order(order_symbol, xrp_open_amt / 4, xrp_current_price, params)
                bot.sendMessage(chat_id=id, text="XRP long profit 1st realize" + "\n" + "long max roe : " + str(xrp_long_max_roe_01) + "\n" + "long roe : " + str(xrp_long_roe_01))
            
            # elif  (xrp_long_qty_01 == xrp_open_amt and xrp_long_max_roe_01 > 0.33 and xrp_long_roe_01 <= 0.3):
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, xrp_open_amt / 4, params)
            #     bot.sendMessage(chat_id=id, text="XRP long profit 1st realize" + "\n" + "long max roe : " + str(xrp_long_max_roe_01) + "\n" + "long roe : " + str(xrp_long_roe_01))

            elif (xrp_long_qty_01 >= (xrp_open_amt * 3) / 4 and xrp_long_qty_01 < xrp_open_amt and
                xrp_long_roe_01 > 1 and
                xrp_ticker_df_01['ma12'][-1] > xrp_ticker_df_01['ema2'][-1]
                ):
                bot.sendMessage(chat_id=id, text="XRP long profit 2nd realize" + "\n" + "long max roe : " + str(xrp_long_max_roe_01) + "\n" + "long roe : " + str(xrp_long_roe_01))

                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, xrp_open_amt / 4, params)

            # elif (xrp_long_qty_01 >= (xrp_open_amt * 3) / 4 and xrp_long_qty_01 < xrp_open_amt and
            #     xrp_long_max_roe_01 > 0.63 and
            #     xrp_long_roe_01 <= 0.6
            #     ):
            #     bot.sendMessage(chat_id=id, text="XRP long profit 2nd realize" + "\n" + "long max roe : " + str(xrp_long_max_roe_01) + "\n" + "long roe : " + str(xrp_long_roe_01))
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, xrp_open_amt / 4, params)

            elif( xrp_long_qty_01 > 0 and xrp_long_max_roe_01 > 1
                and xrp_long_roe_01 <= xrp_long_max_roe_01 * 0.8
                and xrp_ticker_df_01['ma12'][-1] > xrp_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="XRP long profit final realize" + "\n" + "long max roe : " + str(xrp_long_max_roe_01) + "\n" + "long roe : " + str(xrp_long_roe_01))
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, xrp_long_qty_01, params)

                xrp_long_roe_01 = 0
                xrp_long_max_roe_01 = 0

            ###############################################################################################
            # Short. 수익실현
            ###############################################################################################
            if  (xrp_short_qty_01 == xrp_open_amt * -1 and
                xrp_short_roe_01 > 0.5 and
                xrp_ticker_df_01[ 'ma12'][-1] < xrp_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="XRP short profit 1st realize" + "\n" + "short max roe : " + str(xrp_short_max_roe_01) + "\n" + "short roe : " + str(xrp_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_limit_buy_order(order_symbol, xrp_open_amt / 4, xrp_current_price, params)

            # elif  (xrp_short_qty_01 == xrp_open_amt * -1 and
            #     xrp_short_max_roe_01 > 0.33 and
            #     xrp_short_roe_01 <= 0.3):
            #     bot.sendMessage(chat_id=id, text="XRP short profit 1st realize" + "\n" + "short max roe : " + str(xrp_short_max_roe_01) + "\n" + "short roe : " + str(xrp_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, xrp_open_amt / 4, params)

            elif (xrp_short_qty_01 <= ((xrp_open_amt *3) / 4) * -1 and xrp_short_qty_01 > xrp_open_amt * -1 and
                xrp_short_roe_01 > 1 and
                xrp_ticker_df_01['ma12'][-1] < xrp_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="XRP short profit 2nd realize" + "\n" + "short max roe : " + str(xrp_short_max_roe_01) + "\n" + "short roe : " + str(xrp_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, xrp_open_amt / 4, params)

            # elif (xrp_short_qty_01 <= ((xrp_open_amt *3) / 4) * -1 and xrp_short_qty_01 > xrp_open_amt * -1 and
            #     xrp_short_max_roe_01 > 0.63 and
            #     xrp_short_roe_01 <= 0.60):
            #     bot.sendMessage(chat_id=id, text="XRP short profit 2nd realize" + "\n" + "short max roe : " + str(xrp_short_max_roe_01) + "\n" + "short roe : " + str(xrp_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, xrp_open_amt / 4, params)
            
            elif( xrp_short_qty_01 < 0 and xrp_short_max_roe_01 > 1 and
                xrp_short_roe_01 <= xrp_short_max_roe_01 * 0.8 and
                xrp_ticker_df_01['ma12'][-1] < xrp_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="XRP short profit final realize" + "\n" + "short max roe : " + str(xrp_short_max_roe_01) + "\n" + "short roe : " + str(xrp_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, xrp_short_qty_01 * -1, params)

                xrp_short_roe_01 = 0
                xrp_short_max_roe_01 = 0
        
            time.sleep(1)
            # 현재시간
            now = time.localtime()
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print(order_symbol)
            print("long amt      : ", xrp_long_qty_01)
            print("long max roe  : ", xrp_long_max_roe_01)
            print("long roe      : ", xrp_long_roe_01)
            print("short amt     : ", xrp_short_qty_01)
            print("short max roe : ", xrp_short_max_roe_01)
            print("short roe     : ", xrp_short_roe_01)
            print("current price : ", xrp_current_price)
            print("1200ma        : ", round(xrp_ticker_df_01['ma1200'][-1],4))
            print("==================================================")

    def order3(self, bal_symbol, order_symbol, doge_open_amt, doge_leverage):
        if(order_symbol == "DOGE/USDT"):
            global doge_long_loss_cut
            global doge_short_loss_cut
            global doge_long_max_roe_01
            global doge_short_max_roe_01
            global doge_long_roe_01
            global doge_short_roe_01
            global doge_long_open_notice
            global doge_short_open_notice
            # 현재지갑 롱/숏 오픈상태 및 잔액
            balance = binance.fetch_balance(params = {"type" : "future"})
            positions = balance['info']['positions']
            for position in positions:
                if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                    doge_L_position = position
                elif position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                    doge_S_position = position
            doge_long_qty_01 = float(doge_L_position['positionAmt'])
            doge_short_qty_01 = float(doge_S_position['positionAmt'])
            doge_long_entryprice_01 = float(doge_L_position['entryPrice'])
            doge_short_entryprice_01 = float(doge_S_position['entryPrice'])

            markets = binance.load_markets()
            symbol = order_symbol
            market = binance.market(symbol)

            resp = binance.fapiPrivate_post_leverage({'symbol': market['id'],'leverage': doge_leverage})

            doge_1m = binance.fetch_ohlcv(symbol = symbol, timeframe = '1m', since = None, limit = 1201)
            doge_ticker_df_01 = pd.DataFrame(doge_1m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            doge_ticker_df_01['datetime'] = pd.to_datetime(doge_ticker_df_01['datetime'], unit='ms')
            doge_ticker_df_01.set_index('datetime', inplace=True)
            doge_15m = binance.fetch_ohlcv(symbol = symbol, timeframe = '15m', since = None, limit = 50)
            doge_ticker_df_02 = pd.DataFrame(doge_15m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            doge_ticker_df_02['datetime'] = pd.to_datetime(doge_ticker_df_02['datetime'], unit='ms')
            doge_ticker_df_02.set_index('datetime', inplace=True)
            # 단순이평선
            doge_ticker_df_01[ 'ma12'] = doge_ticker_df_01["close"].rolling(window=12).mean()
            doge_ticker_df_01[ 'ma20'] = doge_ticker_df_01["close"].rolling(window=20).mean()
            doge_ticker_df_01['ma120'] = doge_ticker_df_01["close"].rolling(window=120).mean()
            doge_ticker_df_01['ma1200'] = doge_ticker_df_01["close"].rolling(window=1200).mean()
            doge_ticker_df_02[ 'ma36'] = doge_ticker_df_02["close"].rolling(window=50).mean()
            # 지수이평선
            doge_ticker_df_01['ema3'] = doge_ticker_df_01['close'].ewm(span=3).mean()
            doge_ticker_df_01['ema2'] = doge_ticker_df_01['close'].ewm(span=2).mean()
            
            #볼린저밴드 구하기
            doge_ticker_df_01['std20'] = doge_ticker_df_01["close"].rolling(window=20).std()
            doge_ticker_df_01[ 'bu20'] = doge_ticker_df_01[ "ma20"] + doge_ticker_df_01['std20'] * 2
            doge_ticker_df_01[ 'bl20'] = doge_ticker_df_01[ "ma20"] - doge_ticker_df_01['std20'] * 2
            doge_ticker_df_01[ 'bm20'] = (doge_ticker_df_01[ 'bu20'] + doge_ticker_df_01[ 'bl20']) / 2

            doge_std20 = doge_ticker_df_01['std20'] = doge_ticker_df_01['close'].rolling(20).std()
            #doge_stdp = round((doge_std20[-1] / current_price * 100) ,2)
            doge_ticker_df_01['bbu'] = doge_ticker_df_01['ma20'] + doge_ticker_df_01['std20'] * 4
            doge_ticker_df_01['bbl'] = doge_ticker_df_01['ma20'] - doge_ticker_df_01['std20'] * 4

            # 숏 로스컷 : 돈치안20 최대최고
            doge_ticker_df_01[ 'max_high_20'] = doge_ticker_df_01['high'].rolling(20, axis = 0).max() 
            
            # 롱 로스컷 : 돈치안20 최소최저
            doge_ticker_df_01[  'min_low_20'] = doge_ticker_df_01[ 'low'].rolling(20, axis = 0).min()
            
            doge_ticker_df_01[   'middle_20'] = (doge_ticker_df_01['max_high_20'] + doge_ticker_df_01['min_low_20']) / 2

            doge_ticker_df_01.head() # 이거 왜하는지?
            doge_ticker_df_02.head()

            doge_current_price = doge_ticker_df_01['close'][-1]
                        
            if(doge_long_qty_01 > 0):
                doge_long_roe_01 = (doge_current_price - doge_long_entryprice_01) / doge_long_entryprice_01 * 100

            if(doge_long_roe_01 > doge_long_max_roe_01):
                doge_long_max_roe_01 = doge_long_roe_01
            
            if(doge_short_qty_01 < 0):
                doge_short_roe_01 = (doge_short_entryprice_01 - doge_current_price) / doge_short_entryprice_01 * 100
            
            if(doge_short_roe_01 > doge_short_max_roe_01):
                doge_short_max_roe_01 = doge_short_roe_01

            #지정가주문 실패시 시장가주문
            if(doge_long_qty_01 < doge_open_amt and doge_long_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'LONG'}
                data = binance.create_market_buy_order(order_symbol, doge_open_amt - doge_long_qty_01, params)            
                
            if(doge_long_qty_01 > 0 and doge_long_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                        doge_L_position = position
                doge_long_qty_01 = float(doge_L_position['positionAmt'])
                doge_long_entryprice_01 = float(doge_L_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="DOGE Long Open" + "\n" + "entry price : " + str(doge_long_entryprice_01) + "\n" + "amount : " + str(doge_long_qty_01))
                doge_long_open_notice = 0
                
            #지정가주문 실패시 시장가주문
            if(doge_short_qty_01 > doge_open_amt * -1 and doge_short_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'SHORT'}
                data = binance.create_market_sell_order(order_symbol, doge_open_amt + doge_short_qty_01, params)  

            if(doge_short_qty_01 < 0 and doge_short_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                        doge_S_position = position
                doge_short_qty_01 = float(doge_S_position['positionAmt'])
                doge_short_entryprice_01 = float(doge_S_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="DOGE Short Open" + "\n" + "entry price : " + str(doge_short_entryprice_01) + "\n" + "amount : " + str(doge_short_qty_01))
                doge_short_open_notice = 0

            # ###############################################################################################
            # Long. open
            ###############################################################################################
            if (doge_long_qty_01 == 0 and
                doge_ticker_df_01['ema2'][-2] < doge_ticker_df_01['ma1200'][-2] and
                doge_ticker_df_01['ema2'][-1] > doge_ticker_df_01['ma1200'][-1]):
                doge_long_loss_cut = doge_ticker_df_01[  'min_low_20'][-1]
                
                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, doge_open_amt, doge_current_price, params)
                doge_long_open_notice = 1

                if((doge_current_price - doge_long_loss_cut) / doge_current_price < 0.002):
                    doge_long_loss_cut = round(doge_current_price * 0.998,5)
            
            elif (doge_long_qty_01 == 0 and
                doge_ticker_df_01['ema2'][-2] > doge_ticker_df_01['ma1200'][-2] and
                doge_ticker_df_01['low'][-1] < doge_ticker_df_01['ma1200'][-1] and
                doge_current_price > doge_ticker_df_01['ma1200'][-1]):
                doge_long_loss_cut = doge_ticker_df_01[  'min_low_20'][-1]

                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, doge_open_amt, doge_current_price, params)
                doge_long_open_notice = 1

                if((doge_current_price - doge_long_loss_cut) / doge_current_price < 0.002):
                    doge_long_loss_cut = round(doge_current_price * 0.998,5)
            ###############################################################################################
            # Short. open
            ###############################################################################################
            if (doge_short_qty_01 == 0 and
                doge_ticker_df_01['ema2'][-2] > doge_ticker_df_01['ma1200'][-2] and
                doge_ticker_df_01['ema2'][-1] < doge_ticker_df_01['ma1200'][-1]):

                doge_short_loss_cut = doge_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, doge_open_amt, doge_current_price, params)
                doge_short_open_notice = 1

                if((doge_short_loss_cut - doge_current_price) / doge_current_price < 0.002):
                    doge_long_loss_cut = round(doge_current_price * 1.002,5)
            elif (doge_short_qty_01 == 0 and
                doge_ticker_df_01['ema2'][-1] < doge_ticker_df_01['ma1200'][-1] and
                doge_ticker_df_01['high'][-1] > doge_ticker_df_01['ma1200'][-2] and
                doge_current_price < doge_ticker_df_01['ma1200'][-1]):
                doge_short_loss_cut = doge_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, doge_open_amt, doge_current_price, params)
                doge_short_open_notice = 1
                
                if((doge_short_loss_cut - doge_current_price) / doge_current_price < 0.002):
                    doge_long_loss_cut = round(doge_current_price * 1.002,5)
            
            ###############################################################################################
            # Long. 손절
            ###############################################################################################
            if (doge_long_qty_01 > 0 and doge_ticker_df_01['close'][-1] < doge_long_loss_cut):
                bot.sendMessage(chat_id=id, text="Long lose cut" + "\n" + str(doge_long_roe_01) + "\n" + "amount : " + str(doge_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, doge_open_amt, params)
                doge_long_loss_cut = 0
                doge_long_roe_01 = 0
                doge_long_max_roe_01 = 0

            if (doge_long_qty_01 > 0 and doge_long_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="DOGE Long lose cut" + "\n" + str(doge_long_roe_01) + "\n" + "amount : " + str(doge_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, doge_open_amt, params)
                doge_long_loss_cut = 0
                doge_long_roe_01 = 0
                doge_long_max_roe_01 = 0

            if (doge_long_qty_01 > 0 and doge_long_max_roe_01 > 0.55 and 
                doge_current_price <= doge_long_entryprice_01 and doge_current_price < doge_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="DOGE Long 수익실현 후 lose cut" + "\n" + str(doge_long_roe_01) + "\n" + "amount : " + str(doge_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, doge_long_qty_01, params)
                doge_long_loss_cut = 0
                doge_long_roe_01 = 0
                doge_long_max_roe_01 = 0
              
            ###############################################################################################
            # Short. 손절
            ###############################################################################################
            if (doge_short_qty_01 < 0 and
                doge_ticker_df_01['close'][-1] > doge_short_loss_cut):
                bot.sendMessage(chat_id=id, text="DOGE Short lose cut" + "\n" + str(doge_short_roe_01) + "\n" + "amount : " + str(doge_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, doge_open_amt, params)
                doge_short_loss_cut = 50000
                doge_short_roe_01 = 0
                doge_short_max_roe_01 = 0

            if (doge_short_qty_01 < 0 and doge_short_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="DOGE Short lose cut" + "\n" + str(doge_short_roe_01) + "\n" + "amount : " + str(doge_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, doge_open_amt, params)

                doge_short_loss_cut = 50000
                doge_short_roe_01 = 0
                doge_short_max_roe_01 = 0

            if (doge_short_qty_01 < 0 and doge_short_max_roe_01 > 0.55 and
                 doge_current_price >= doge_short_entryprice_01 and doge_current_price > doge_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="DOGE Short 수익실현 후 lose cut" + "\n" + str(doge_short_roe_01) + "\n" + "amount : " + str(doge_short_qty_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, doge_short_qty_01 * -1, params)

                doge_short_loss_cut = 50000
                doge_short_roe_01 = 0
                doge_short_max_roe_01 = 0

            ###############################################################################################
            # Long. 수익실현
            ###############################################################################################
            if  (
                doge_long_qty_01 == doge_open_amt and
                doge_long_roe_01 > 0.5 and
                doge_ticker_df_01['ma12'][-1] > doge_ticker_df_01['ema2'][-1]
                ):
                params = {'positionSide' : 'LONG'}
                data = binance.create_limit_sell_order(order_symbol, doge_open_amt / 4, doge_current_price, params)
                bot.sendMessage(chat_id=id, text="DOGE long profit 1st realize" + "\n" + "long max roe : " + str(doge_long_max_roe_01) + "\n" + "long roe : " + str(doge_long_roe_01))
            
            # elif  (doge_long_qty_01 == doge_open_amt and doge_long_max_roe_01 > 0.33 and doge_long_roe_01 <= 0.3):
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, doge_open_amt / 4, params)
            #     bot.sendMessage(chat_id=id, text="DOGE long profit 1st realize" + "\n" + "long max roe : " + str(doge_long_max_roe_01) + "\n" + "long roe : " + str(doge_long_roe_01))

            elif (doge_long_qty_01 >= (doge_open_amt * 3) / 4 and doge_long_qty_01 < doge_open_amt and
                doge_long_roe_01 > 1 and
                doge_ticker_df_01['ma12'][-1] > doge_ticker_df_01['ema2'][-1]
                ):
                bot.sendMessage(chat_id=id, text="DOGE long profit 2nd realize" + "\n" + "long max roe : " + str(doge_long_max_roe_01) + "\n" + "long roe : " + str(doge_long_roe_01))

                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, doge_open_amt / 4, params)

            # elif (doge_long_qty_01 >= (doge_open_amt * 3) / 4 and doge_long_qty_01 < doge_open_amt and
            #     doge_long_max_roe_01 > 0.63 and
            #     doge_long_roe_01 <= 0.6
            #     ):
            #     bot.sendMessage(chat_id=id, text="DOGE long profit 2nd realize" + "\n" + "long max roe : " + str(doge_long_max_roe_01) + "\n" + "long roe : " + str(doge_long_roe_01))
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, doge_open_amt / 4, params)

            elif( doge_long_qty_01 > 0 and doge_long_max_roe_01 > 1
                and doge_long_roe_01 <= doge_long_max_roe_01 * 0.8
                and doge_ticker_df_01['ma12'][-1] > doge_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="DOGE long profit final realize" + "\n" + "long max roe : " + str(doge_long_max_roe_01) + "\n" + "long roe : " + str(doge_long_roe_01))
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, doge_long_qty_01, params)

                doge_long_roe_01 = 0
                doge_long_max_roe_01 = 0

            ###############################################################################################
            # Short. 수익실현
            ###############################################################################################
            if  (doge_short_qty_01 == doge_open_amt * -1 and
                doge_short_roe_01 > 0.5 and
                doge_ticker_df_01[ 'ma12'][-1] < doge_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="DOGE short profit 1st realize" + "\n" + "short max roe : " + str(doge_short_max_roe_01) + "\n" + "short roe : " + str(doge_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_limit_buy_order(order_symbol, doge_open_amt / 4, doge_current_price, params)

            # elif  (doge_short_qty_01 == doge_open_amt * -1 and
            #     doge_short_max_roe_01 > 0.33 and
            #     doge_short_roe_01 <= 0.3):
            #     bot.sendMessage(chat_id=id, text="DOGE short profit 1st realize" + "\n" + "short max roe : " + str(doge_short_max_roe_01) + "\n" + "short roe : " + str(doge_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, doge_open_amt / 4, params)

            elif (doge_short_qty_01 <= ((doge_open_amt *3) / 4) * -1 and doge_short_qty_01 > doge_open_amt * -1 and
                doge_short_roe_01 > 1 and
                doge_ticker_df_01['ma12'][-1] < doge_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="DOGE short profit 2nd realize" + "\n" + "short max roe : " + str(doge_short_max_roe_01) + "\n" + "short roe : " + str(doge_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, doge_open_amt / 4, params)

            # elif (doge_short_qty_01 <= ((doge_open_amt *3) / 4) * -1 and doge_short_qty_01 > doge_open_amt * -1 and
            #     doge_short_max_roe_01 > 0.63 and
            #     doge_short_roe_01 <= 0.60):
            #     bot.sendMessage(chat_id=id, text="DOGE short profit 2nd realize" + "\n" + "short max roe : " + str(doge_short_max_roe_01) + "\n" + "short roe : " + str(doge_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, doge_open_amt / 4, params)
            
            elif( doge_short_qty_01 < 0 and doge_short_max_roe_01 > 1 and
                doge_short_roe_01 <= doge_short_max_roe_01 * 0.8 and
                doge_ticker_df_01['ma12'][-1] < doge_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="DOGE short profit final realize" + "\n" + "short max roe : " + str(doge_short_max_roe_01) + "\n" + "short roe : " + str(doge_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, doge_short_qty_01 * -1, params)

                doge_short_roe_01 = 0
                doge_short_max_roe_01 = 0
        
            time.sleep(1)
            # 현재시간
            now = time.localtime()
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print(order_symbol)
            print("long amt      : ", doge_long_qty_01)
            print("long max roe  : ", doge_long_max_roe_01)
            print("long roe      : ", doge_long_roe_01)
            print("short amt     : ", doge_short_qty_01)
            print("short max roe : ", doge_short_max_roe_01)
            print("short roe     : ", doge_short_roe_01)
            print("current price : ", doge_current_price)
            print("1200ma        : ", round(doge_ticker_df_01['ma1200'][-1],5))
            print("==================================================")

    def order4(self, bal_symbol, order_symbol, eth_open_amt, eth_leverage):
        if(order_symbol == "ETH/USDT"):
            global eth_long_loss_cut
            global eth_short_loss_cut
            global eth_long_max_roe_01
            global eth_short_max_roe_01
            global eth_long_roe_01
            global eth_short_roe_01
            global eth_long_open_notice
            global eth_short_open_notice
            # 현재지갑 롱/숏 오픈상태 및 잔액
            balance = binance.fetch_balance(params = {"type" : "future"})
            positions = balance['info']['positions']
            for position in positions:
                if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                    eth_L_position = position
                elif position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                    eth_S_position = position
            eth_long_qty_01 = float(eth_L_position['positionAmt'])
            eth_short_qty_01 = float(eth_S_position['positionAmt'])
            eth_long_entryprice_01 = float(eth_L_position['entryPrice'])
            eth_short_entryprice_01 = float(eth_S_position['entryPrice'])

            markets = binance.load_markets()
            symbol = order_symbol
            market = binance.market(symbol)

            resp = binance.fapiPrivate_post_leverage({'symbol': market['id'],'leverage': eth_leverage})

            eth_1m = binance.fetch_ohlcv(symbol = symbol, timeframe = '1m', since = None, limit = 1201)
            eth_ticker_df_01 = pd.DataFrame(eth_1m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            eth_ticker_df_01['datetime'] = pd.to_datetime(eth_ticker_df_01['datetime'], unit='ms')
            eth_ticker_df_01.set_index('datetime', inplace=True)
            eth_15m = binance.fetch_ohlcv(symbol = symbol, timeframe = '15m', since = None, limit = 50)
            eth_ticker_df_02 = pd.DataFrame(eth_15m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            eth_ticker_df_02['datetime'] = pd.to_datetime(eth_ticker_df_02['datetime'], unit='ms')
            eth_ticker_df_02.set_index('datetime', inplace=True)
            # 단순이평선
            eth_ticker_df_01[ 'ma12'] = eth_ticker_df_01["close"].rolling(window=12).mean()
            eth_ticker_df_01[ 'ma20'] = eth_ticker_df_01["close"].rolling(window=20).mean()
            eth_ticker_df_01['ma120'] = eth_ticker_df_01["close"].rolling(window=120).mean()
            eth_ticker_df_01['ma1200'] = eth_ticker_df_01["close"].rolling(window=1200).mean()
            eth_ticker_df_02[ 'ma36'] = eth_ticker_df_02["close"].rolling(window=50).mean()
            # 지수이평선
            eth_ticker_df_01['ema3'] = eth_ticker_df_01['close'].ewm(span=3).mean()
            eth_ticker_df_01['ema2'] = eth_ticker_df_01['close'].ewm(span=2).mean()
            
            #볼린저밴드 구하기
            eth_ticker_df_01['std20'] = eth_ticker_df_01["close"].rolling(window=20).std()
            eth_ticker_df_01[ 'bu20'] = eth_ticker_df_01[ "ma20"] + eth_ticker_df_01['std20'] * 2
            eth_ticker_df_01[ 'bl20'] = eth_ticker_df_01[ "ma20"] - eth_ticker_df_01['std20'] * 2
            eth_ticker_df_01[ 'bm20'] = (eth_ticker_df_01[ 'bu20'] + eth_ticker_df_01[ 'bl20']) / 2

            eth_std20 = eth_ticker_df_01['std20'] = eth_ticker_df_01['close'].rolling(20).std()
            #eth_stdp = round((eth_std20[-1] / current_price * 100) ,2)
            eth_ticker_df_01['bbu'] = eth_ticker_df_01['ma20'] + eth_ticker_df_01['std20'] * 4
            eth_ticker_df_01['bbl'] = eth_ticker_df_01['ma20'] - eth_ticker_df_01['std20'] * 4

            # 숏 로스컷 : 돈치안20 최대최고
            eth_ticker_df_01[ 'max_high_20'] = eth_ticker_df_01['high'].rolling(20, axis = 0).max() 
            
            # 롱 로스컷 : 돈치안20 최소최저
            eth_ticker_df_01[  'min_low_20'] = eth_ticker_df_01[ 'low'].rolling(20, axis = 0).min()
            
            eth_ticker_df_01[   'middle_20'] = (eth_ticker_df_01['max_high_20'] + eth_ticker_df_01['min_low_20']) / 2

            eth_ticker_df_01.head() # 이거 왜하는지?
            eth_ticker_df_02.head()

            eth_current_price = eth_ticker_df_01['close'][-1]
                        
            if(eth_long_qty_01 > 0):
                eth_long_roe_01 = (eth_current_price - eth_long_entryprice_01) / eth_long_entryprice_01 * 100

            if(eth_long_roe_01 > eth_long_max_roe_01):
                eth_long_max_roe_01 = eth_long_roe_01
            
            if(eth_short_qty_01 < 0):
                eth_short_roe_01 = (eth_short_entryprice_01 - eth_current_price) / eth_short_entryprice_01 * 100
            
            if(eth_short_roe_01 > eth_short_max_roe_01):
                eth_short_max_roe_01 = eth_short_roe_01

            #지정가주문 실패시 시장가주문
            if(eth_long_qty_01 < eth_open_amt and eth_long_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'LONG'}
                data = binance.create_market_buy_order(order_symbol, eth_open_amt - eth_long_qty_01, params)            
                
            if(eth_long_qty_01 > 0 and eth_long_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "LONG":
                        eth_L_position = position
                eth_long_qty_01 = float(eth_L_position['positionAmt'])
                eth_long_entryprice_01 = float(eth_L_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="ETH Long Open" + "\n" + "entry price : " + str(eth_long_entryprice_01) + "\n" + "amount : " + str(eth_long_qty_01))
                eth_long_open_notice = 0
                
            #지정가주문 실패시 시장가주문
            if(eth_short_qty_01 > eth_open_amt * -1 and eth_short_open_notice == 1):
                binance.cancel_all_orders(order_symbol, params)
                time.sleep(1)
                params = {'positionSide': 'SHORT'}
                data = binance.create_market_sell_order(order_symbol, eth_open_amt + eth_short_qty_01, params)  

            if(eth_short_qty_01 < 0 and eth_short_open_notice == 1):
                for position in positions:
                    if position["symbol"] == bal_symbol and position["positionSide"] == "SHORT":
                        eth_S_position = position
                eth_short_qty_01 = float(eth_S_position['positionAmt'])
                eth_short_entryprice_01 = float(eth_S_position['entryPrice'])
                bot.sendMessage(chat_id=id, text="ETH Short Open" + "\n" + "entry price : " + str(eth_short_entryprice_01) + "\n" + "amount : " + str(eth_short_qty_01))
                eth_short_open_notice = 0

            # ###############################################################################################
            # Long. open
            ###############################################################################################
            if (eth_long_qty_01 == 0 and
                eth_ticker_df_01['ema2'][-2] < eth_ticker_df_01['ma1200'][-2] and
                eth_ticker_df_01['ema2'][-1] > eth_ticker_df_01['ma1200'][-1]):
                eth_long_loss_cut = eth_ticker_df_01[  'min_low_20'][-1]
                
                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, eth_open_amt, eth_current_price, params)
                eth_long_open_notice = 1

                if((eth_current_price - eth_long_loss_cut) / eth_current_price < 0.002):
                    eth_long_loss_cut = round(eth_current_price * 0.998,2)
            
            elif (eth_long_qty_01 == 0 and
                eth_ticker_df_01['ema2'][-2] > eth_ticker_df_01['ma1200'][-2] and
                eth_ticker_df_01['low'][-1] < eth_ticker_df_01['ma1200'][-1] and
                eth_current_price > eth_ticker_df_01['ma1200'][-1]):
                eth_long_loss_cut = eth_ticker_df_01[  'min_low_20'][-1]

                params = {'positionSide': 'LONG'}
                data = binance.create_limit_buy_order(order_symbol, eth_open_amt, eth_current_price, params)
                eth_long_open_notice = 1

                if((eth_current_price - eth_long_loss_cut) / eth_current_price < 0.002):
                    eth_long_loss_cut = round(eth_current_price * 0.998,2)
            ###############################################################################################
            # Short. open
            ###############################################################################################
            if (eth_short_qty_01 == 0 and
                eth_ticker_df_01['ema2'][-2] > eth_ticker_df_01['ma1200'][-2] and
                eth_ticker_df_01['ema2'][-1] < eth_ticker_df_01['ma1200'][-1]):

                eth_short_loss_cut = eth_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, eth_open_amt, eth_current_price, params)
                eth_short_open_notice = 1

                if((eth_short_loss_cut - eth_current_price) / eth_current_price < 0.002):
                    eth_long_loss_cut = round(eth_current_price * 1.002,2)
            elif (eth_short_qty_01 == 0 and
                eth_ticker_df_01['ema2'][-1] < eth_ticker_df_01['ma1200'][-1] and
                eth_ticker_df_01['high'][-1] > eth_ticker_df_01['ma1200'][-2] and
                eth_current_price < eth_ticker_df_01['ma1200'][-1]):
                eth_short_loss_cut = eth_ticker_df_01['max_high_20'][-1]

                params = {'positionSide': 'SHORT'}
                data = binance.create_limit_sell_order(order_symbol, eth_open_amt, eth_current_price, params)
                eth_short_open_notice = 1
                
                if((eth_short_loss_cut - eth_current_price) / eth_current_price < 0.002):
                    eth_long_loss_cut = round(eth_current_price * 1.002,2)
            
            ###############################################################################################
            # Long. 손절
            ###############################################################################################
            if (eth_long_qty_01 > 0 and eth_ticker_df_01['close'][-1] < eth_long_loss_cut):
                bot.sendMessage(chat_id=id, text="Long lose cut" + "\n" + str(eth_long_roe_01) + "\n" + "amount : " + str(eth_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, eth_open_amt, params)
                eth_long_loss_cut = 0
                eth_long_roe_01 = 0
                eth_long_max_roe_01 = 0

            if (eth_long_qty_01 > 0 and eth_long_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="ETH Long lose cut" + "\n" + str(eth_long_roe_01) + "\n" + "amount : " + str(eth_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, eth_open_amt, params)
                eth_long_loss_cut = 0
                eth_long_roe_01 = 0
                eth_long_max_roe_01 = 0

            if (eth_long_qty_01 > 0 and eth_long_max_roe_01 > 0.55 and
                eth_current_price <= eth_long_entryprice_01 and eth_current_price < eth_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="ETH Long 수익실현 후 lose cut" + "\n" + str(eth_long_roe_01) + "\n" + "amount : " + str(eth_long_qty_01))            
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, eth_long_qty_01, params)
                eth_long_loss_cut = 0
                eth_long_roe_01 = 0
                eth_long_max_roe_01 = 0
              
            ###############################################################################################
            # Short. 손절
            ###############################################################################################
            if (eth_short_qty_01 < 0 and
                eth_ticker_df_01['close'][-1] > eth_short_loss_cut):
                bot.sendMessage(chat_id=id, text="ETH Short lose cut" + "\n" + str(eth_short_roe_01) + "\n" + "amount : " + str(eth_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, eth_open_amt, params)
                eth_short_loss_cut = 50000
                eth_short_roe_01 = 0
                eth_short_max_roe_01 = 0

            if (eth_short_qty_01 < 0 and eth_short_roe_01 < -0.5):
                bot.sendMessage(chat_id=id, text="ETH Short lose cut" + "\n" + str(eth_short_roe_01) + "\n" + "amount : " + str(eth_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, eth_open_amt, params)

                eth_short_loss_cut = 50000
                eth_short_roe_01 = 0
                eth_short_max_roe_01 = 0

            if (eth_short_qty_01 < 0 and eth_short_max_roe_01 > 0.55 and
                eth_current_price >= eth_short_entryprice_01 and eth_current_price > eth_ticker_df_01['ma1200'][-1]):
                bot.sendMessage(chat_id=id, text="ETH Short 수익실현 후 lose cut" + "\n" + str(eth_short_roe_01) + "\n" + "amount : " + str(eth_short_qty_01))            
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, eth_short_qty_01 * -1, params)
                eth_short_loss_cut = 50000
                eth_short_roe_01 = 0
                eth_short_max_roe_01 = 0

            ###############################################################################################
            # Long. 수익실현
            ###############################################################################################
            if  (
                eth_long_qty_01 == eth_open_amt and
                eth_long_roe_01 > 0.5 and
                eth_ticker_df_01['ma12'][-1] > eth_ticker_df_01['ema2'][-1]
                ):
                params = {'positionSide' : 'LONG'}
                data = binance.create_limit_sell_order(order_symbol, eth_open_amt / 4, eth_current_price, params)
                bot.sendMessage(chat_id=id, text="ETH long profit 1st realize" + "\n" + "long max roe : " + str(eth_long_max_roe_01) + "\n" + "long roe : " + str(eth_long_roe_01))
            
            # elif  (eth_long_qty_01 == eth_open_amt and eth_long_max_roe_01 > 0.33 and eth_long_roe_01 <= 0.3):
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, eth_open_amt / 4, params)
            #     bot.sendMessage(chat_id=id, text="ETH long profit 1st realize" + "\n" + "long max roe : " + str(eth_long_max_roe_01) + "\n" + "long roe : " + str(eth_long_roe_01))

            elif (eth_long_qty_01 >= (eth_open_amt * 3) / 4 and eth_long_qty_01 < eth_open_amt and
                eth_long_roe_01 > 1 and
                eth_ticker_df_01['ma12'][-1] > eth_ticker_df_01['ema2'][-1]
                ):
                bot.sendMessage(chat_id=id, text="ETH long profit 2nd realize" + "\n" + "long max roe : " + str(eth_long_max_roe_01) + "\n" + "long roe : " + str(eth_long_roe_01))

                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, eth_open_amt / 4, params)

            # elif (eth_long_qty_01 >= (eth_open_amt * 3) / 4 and eth_long_qty_01 < eth_open_amt and
            #     eth_long_max_roe_01 > 0.63 and
            #     eth_long_roe_01 <= 0.6
            #     ):
            #     bot.sendMessage(chat_id=id, text="ETH long profit 2nd realize" + "\n" + "long max roe : " + str(eth_long_max_roe_01) + "\n" + "long roe : " + str(eth_long_roe_01))
            #     params = {'positionSide' : 'LONG'}
            #     data = binance.create_market_sell_order(order_symbol, eth_open_amt / 4, params)

            elif( eth_long_qty_01 > 0 and eth_long_max_roe_01 > 1
                and eth_long_roe_01 <= eth_long_max_roe_01 * 0.8
                and eth_ticker_df_01['ma12'][-1] > eth_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="ETH long profit final realize" + "\n" + "long max roe : " + str(eth_long_max_roe_01) + "\n" + "long roe : " + str(eth_long_roe_01))
                params = {'positionSide' : 'LONG'}
                data = binance.create_market_sell_order(order_symbol, eth_long_qty_01, params)

                eth_long_roe_01 = 0
                eth_long_max_roe_01 = 0

            ###############################################################################################
            # Short. 수익실현
            ###############################################################################################
            if  (eth_short_qty_01 == eth_open_amt * -1 and
                eth_short_roe_01 > 0.5 and
                eth_ticker_df_01[ 'ma12'][-1] < eth_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="ETH short profit 1st realize" + "\n" + "short max roe : " + str(eth_short_max_roe_01) + "\n" + "short roe : " + str(eth_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_limit_buy_order(order_symbol, eth_open_amt / 4, eth_current_price, params)

            # elif  (eth_short_qty_01 == eth_open_amt * -1 and
            #     eth_short_max_roe_01 > 0.33 and
            #     eth_short_roe_01 <= 0.3):
            #     bot.sendMessage(chat_id=id, text="ETH short profit 1st realize" + "\n" + "short max roe : " + str(eth_short_max_roe_01) + "\n" + "short roe : " + str(eth_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, eth_open_amt / 4, params)

            elif (eth_short_qty_01 <= ((eth_open_amt *3) / 4) * -1 and eth_short_qty_01 > eth_open_amt * -1 and
                eth_short_roe_01 > 1 and
                eth_ticker_df_01['ma12'][-1] < eth_ticker_df_01['ema2'][-1]):
                bot.sendMessage(chat_id=id, text="ETH short profit 2nd realize" + "\n" + "short max roe : " + str(eth_short_max_roe_01) + "\n" + "short roe : " + str(eth_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, eth_open_amt / 4, params)

            # elif (eth_short_qty_01 <= ((eth_open_amt *3) / 4) * -1 and eth_short_qty_01 > eth_open_amt * -1 and
            #     eth_short_max_roe_01 > 0.63 and
            #     eth_short_roe_01 <= 0.60):
            #     bot.sendMessage(chat_id=id, text="ETH short profit 2nd realize" + "\n" + "short max roe : " + str(eth_short_max_roe_01) + "\n" + "short roe : " + str(eth_short_roe_01))
            #     params = {'positionSide' : 'SHORT'}
            #     data = binance.create_market_buy_order(order_symbol, eth_open_amt / 4, params)
            
            elif( eth_short_qty_01 < 0 and eth_short_max_roe_01 > 1 and
                eth_short_roe_01 <= eth_short_max_roe_01 * 0.8 and
                eth_ticker_df_01['ma12'][-1] < eth_ticker_df_01['ema2'][-1]):
                
                bot.sendMessage(chat_id=id, text="ETH short profit final realize" + "\n" + "short max roe : " + str(eth_short_max_roe_01) + "\n" + "short roe : " + str(eth_short_roe_01))
                params = {'positionSide' : 'SHORT'}
                data = binance.create_market_buy_order(order_symbol, eth_short_qty_01 * -1, params)

                eth_short_roe_01 = 0
                eth_short_max_roe_01 = 0
        
            time.sleep(1)
            # 현재시간
            now = time.localtime()
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print(order_symbol)
            print("long amt      : ", eth_long_qty_01)
            print("long max roe  : ", eth_long_max_roe_01)
            print("long roe      : ", eth_long_roe_01)
            print("short amt     : ", eth_short_qty_01)
            print("short max roe : ", eth_short_max_roe_01)
            print("short roe     : ", eth_short_roe_01)
            print("current price : ", eth_current_price)
            print("1200ma        : ", round(eth_ticker_df_01['ma1200'][-1],2))
            print("==================================================")







go = Mybinance()

while True:
    try:
#     def order(self, bal_symbol, order_symbol, btc_open_amt, btc_leverage):
        go.order("BTCUSDT", "BTC/USDT", 0.01, 10)
        go.order2("XRPUSDT", "XRP/USDT", 1000, 10)
        go.order3("DOGEUSDT", "DOGE/USDT", 4000, 10)
        go.order4("ETHUSDT", "ETH/USDT", 0.3, 10)
    except:
        pass

# go.order("BTCUSDT", "BTC/USDT", 0.01, 10)
# go.order2("XRPUSDT", "XRP/USDT", 1000, 10)
# go.order3("DOGEUSDT", "DOGE/USDT", 4000, 10)
# go.order4("ETHUSDT", "ETH/USDT", 0.3, 10)

