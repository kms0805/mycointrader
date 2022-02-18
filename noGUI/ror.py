import pyupbit
import numpy as np

class Best_k:
    def __init__(self):
        self.best_k = 0.5
        self.best_ror = -1

    def get_ror(self, k):
        df = pyupbit.get_ohlcv("KRW-BTC", count=7)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)

        ror = df['ror'].cumprod()[-2]
        return ror

    def get_best_k(self, is_print = False):
        for k in np.arange(0.1, 1.0, 0.1):
            ror = self.get_ror(k)
            if is_print:
                print("%.1f %f" % (k, ror))
            if ror > self.best_ror:
                self.best_ror = ror
                self.best_k = k


if __name__ == '__main__':
    b = Best_k()
    b.get_best_k(True)