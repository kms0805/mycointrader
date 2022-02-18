import time
import pyupbit
import datetime
import ror
import schedule

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5
def get_balance(ticker, upbit):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0
def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


def main():
    # 로그인
    with open("../key/upbit.txt") as f:
        lines = f.readlines()
        access = lines[0].strip()
        secret = lines[1].strip()
    try:
        upbit = pyupbit.Upbit(access, secret)
    except:
        print("login error")

    # 자동매매 시작
    print("start")
    kFinder = ror.Best_k()
    schedule.every().day.at("08:30").do(lambda: kFinder.get_best_k())

    while True:
        try:
            now = datetime.datetime.now()
            start_time = get_start_time("KRW-BTC")
            end_time = start_time + datetime.timedelta(days=1)
            schedule.run_pending()

            if start_time < now < end_time - datetime.timedelta(seconds=10):
                target_price = get_target_price("KRW-BTC", kFinder.best_k)
                ma5 = get_ma5("KRW-BTC")
                current_price = get_current_price("KRW-BTC")
                if target_price < current_price and ma5 < current_price:
                    krw = get_balance("KRW",upbit)
                    if krw > 5000:
                        upbit.buy_market_order("KRW-BTC", krw*0.9995)
                        print(f'[buy] time: {now}, krw : {krw*0.9995:,.1}')
            else:
                btc = get_balance("BTC",upbit)
                if btc > 0.00008:
                    upbit.sell_market_order("KRW-BTC", btc*0.9995)
                    print(f'[sell] time: {now}, btc:{btc*0.9995:,.1}')
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
if __name__ == '__main__':
    main()