import pyupbit as pu
from time import sleep

access = "inr9qYtQVDrNEx4b5JEw32j6RK8ubSFootMm6EEz"
secret = "r9xQL5aZgQYdTXgeHWdys8jEhnFzdnnmxwd7ZSxF"

my_account = pu.Upbit(access, secret)

class Myupbit():
    #생성자 (초기에 딱 한번 설정을 해주는 역할)
    def __init__(self):
        print("시작")
        self.is_buy = False
  
    def watch_and_order(self, symbol, money):
        price = pu.get_current_price(symbol)
        print(f"{symbol}의 현재가격은 {price}원 입니다.")
        print("진행중")
        avg = my_account.get_avg_buy_price(symbol)        
        df = pu.get_ohlcv(ticker = symbol, interval= "minute5", count=20)
        df['MA'] = df["close"].rolling(window=20).mean()
        df.head(20)
        sma = df.MA[-1]
        # print(f"{symbol}의 5분봉 20이평값은 {sma}원 입니다.")    

        if price < sma * 0.991 and not self.is_buy:
            # print("3초대기")
            # sleep(3)
            # print("3초대기 끝")
            my_account.buy_market_order(symbol, money, 1)
            sleep(1)
            print(f"{symbol}를 {avg}에 매수")
            self.is_buy = True
            

    def watch_and_sell(self, symbol):
        price = pu.get_current_price(symbol)
        df = pu.get_ohlcv(ticker = symbol, interval= "minute5", count=20)
        df['MA'] = df["close"].rolling(window=20).mean()
        df.head(20)
        sma = df.MA[-1]
        amount = my_account.get_balance(symbol)
        avg = my_account.get_avg_buy_price(symbol)
        print(f"{symbol}의 현재 보유량은 {amount}이고, 평단가는 {avg}입니다.")
        
        if price > sma * 1.009 and self.is_buy:
            # t1_price = price
            # t2_price = price
            # while t1_price <= t2_price:
            #     t1_price = price
            #     print("상승추세이기 때문에 30초 기다립니다.")
            #     sleep(30)
            #     t2_price = price
                
            my_account.sell_market_order(symbol, amount)
            self.is_buy = False
            print(f"{symbol} 조건만족 매도")


        elif price < avg * 0.97 and self.is_buy:
            my_account.sell_market_order(symbol, amount)
            self.is_buy = False
            print(f"{symbol} 3%손실매도")


go = Myupbit()

while True:
    go.watch_and_order("KRW-XRP", 100000)
    go.watch_and_sell("KRW-XRP")
    go.watch_and_order("KRW-CHZ", 100000)
    go.watch_and_sell("KRW-CHZ")
    go.watch_and_order("KRW-DAWN", 100000)
    go.watch_and_sell("KRW-DAWN")
    
