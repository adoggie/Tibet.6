#coding:utf-8

import talib
import numpy as np

########################################################################
class ArrayManager(object):
    """
    K线序列管理工具，负责：
    1. K线时间序列的维护
    2. 常用技术指标的计算
    """

    # ----------------------------------------------------------------------
    def __init__(self, size=100):
        """Constructor"""
        self.count = 0  # 缓存计数
        self.size = size  # 缓存大小
        self.inited = False  # True if count>=size

        self.openArray = np.zeros(size)  # OHLC
        self.highArray = np.zeros(size)
        self.lowArray = np.zeros(size)
        self.closeArray = np.zeros(size)
        self.volumeArray = np.zeros(size)

    # ----------------------------------------------------------------------
    def updateBar(self, bar):
        """更新K线"""
        self.count += 1
        if not self.inited and self.count >= self.size:
            self.inited = True

        self.openArray[0:self.size - 1] = self.openArray[1:self.size]
        self.highArray[0:self.size - 1] = self.highArray[1:self.size]
        self.lowArray[0:self.size - 1] = self.lowArray[1:self.size]
        self.closeArray[0:self.size - 1] = self.closeArray[1:self.size]
        self.volumeArray[0:self.size - 1] = self.volumeArray[1:self.size]

        self.openArray[-1] = bar.open
        self.highArray[-1] = bar.high
        self.lowArray[-1] = bar.low
        self.closeArray[-1] = bar.close
        self.volumeArray[-1] = bar.volume

    def setCloseArray(self, close):
        self.closeArray = np.array(close,dtype=np.double)
        return self
    # ----------------------------------------------------------------------
    @property
    def open(self):
        """获取开盘价序列"""
        return self.openArray

    # ----------------------------------------------------------------------
    @property
    def high(self):
        """获取最高价序列"""
        return self.highArray

    # ----------------------------------------------------------------------
    @property
    def low(self):
        """获取最低价序列"""
        return self.lowArray

    # ----------------------------------------------------------------------
    @property
    def close(self):
        """获取收盘价序列"""
        return self.closeArray

    # ----------------------------------------------------------------------
    @property
    def volume(self):
        """获取成交量序列"""
        return self.volumeArray

    # ----------------------------------------------------------------------
    def ma(self, n, array=False):
        """简单均线"""
        result = talib.MA(self.close, n)
        if array:
            return result
        return result[-1]

    def sma(self, n, array=False):
        """简单均线"""
        result = talib.SMA(self.close, n)
        if array:
            return result
        return result[-1]

    # ----------------------------------------------------------------------
    def std(self, n, array=False):
        """标准差 , compare with tdx ,okay"""
        import pandas as pd

        # result = talib.STDDEV(self.close, timeperiod=n, nbdev=0)
        result = pd.Series(self.close).rolling(window=n,center=False).std().values

        # result = np.std(self.close, ddof = 1)
        # result = np.sqrt(((self.close - np.mean(self.close)) ** 2).sum() / (self.close.size - 1))
        if array:
            return result
        return result[-1]

    # ----------------------------------------------------------------------
    def cci(self, n, array=False):
        """CCI指标"""
        result = talib.CCI(self.high, self.low, self.close, n)
        if array:
            return result
        return result[-1]

    # ----------------------------------------------------------------------
    def atr(self, n, array=False):
        """ATR指标"""
        result = talib.ATR(self.high, self.low, self.close, n)
        if array:
            return result
        return result[-1]

    # ----------------------------------------------------------------------
    def rsi(self, n, array=False):
        """RSI指标 常用周期: 6,12,24 , 采样数量: 100 -200 ,
        周期24需200采样数，否则出现偏离（参考通达信rsi指标计算）"""
        result = talib.RSI(self.close, n)
        if array:
            return result
        return result[-1]

    # ----------------------------------------------------------------------
    def macd(self, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9, array=False):
        """MACD指标
        fastperiod=12, slowperiod=26, signalperiod=9
        """
        macd, signal, hist = talib.MACD(self.close, fastPeriod,
                                        slowPeriod, signalPeriod)
        if array:
            return macd, signal, hist
        return macd[-1], signal[-1], hist[-1]

    # ----------------------------------------------------------------------
    def adx(self, n, array=False):
        """ADX指标"""
        result = talib.ADX(self.high, self.low, self.close, n)
        if array:
            return result
        return result[-1]

    # ----------------------------------------------------------------------
    def boll(self, n, dev, array=False):
        """布林通道
        n - bollWindow = 18                     # 布林通道窗口数
        dev - bollDev = 3.4                       # 布林通道的偏差
        dev 幾倍標準差 默認2倍
        """
        # mid = self.sma(n, array)
        mid = self.ma(n, array)
        std = self.std(n, array)

        up = mid + std * dev
        down = mid - std * dev

        return up, down

        # ----------------------------------------------------------------------

    def keltner(self, n, dev, array=False):
        """肯特纳通道"""
        mid = self.sma(n, array)
        atr = self.atr(n, array)

        up = mid + atr * dev
        down = mid - atr * dev

        return up, down

    # ----------------------------------------------------------------------
    def donchian(self, n, array=False):
        """唐奇安通道"""
        up = talib.MAX(self.high, n)
        down = talib.MIN(self.low, n)

        if array:
            return up, down
        return up[-1], down[-1]


def kdj(high, low, close, n=9, M1=3, M2=3, array=False):
    '''
    :param:
        high,low,close : 價格序列 list
        n，时间长度
    :returns  
    指数加权滑动（ewm）, 指数加权滑动平均（ewma）
    http://pandas.pydata.org/pandas-docs/version/0.17.0/generated/pandas.ewma.html
    '''
    import pandas as pd

    df = pd.DataFrame(dict(high=high, low=low, close=close))
    # lowList = pd.rolling_min(df['low'], n)
    lowList = df['low'].rolling(window=n, center=False).min()
    # lowList.fillna(value=pd.expanding_min(df['low']), inplace=True)
    lowList.fillna(value=df['low'].rolling(window=9,center=False).max(), inplace=True)
    # highList = pd.rolling_max(df['high'], n)
    highList = df['high'].rolling(window=n,center=False).max()

    # highList.fillna(value=pd.expanding_max(df['high']), inplace=True)
    highList.fillna(value= df['high'].expanding(min_periods=1).max(), inplace=True)
    rsv = (df['close'] - lowList) / (highList - lowList) * 100

    # k = pd.ewma(rsv, com=M1 - 1)
    k = rsv.ewm(ignore_na=False, min_periods=0, adjust=True, com=M1-1).mean()
    # d = pd.ewma(k, com=M2 - 1)
    d = k.ewm(ignore_na=False, min_periods=0, adjust=True, com=M2 - 1).mean()
    j = 3.0 * k - 2.0 * d

    if not array:
        return k.values[-1], d.values[-1], j.values[-1]
    return k.values, d.values, j.values