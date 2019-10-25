#coding:utf-8

"""
zf_inday.py

日内涨跌幅度
"""

import numpy as np
import talib as ta
from mantis.sg.fisher import stbase
from mantis.sg.fisher import stalgorithm
from base import StrategyEntity


class SimpleMACD(StrategyEntity):
    def __init__(self,strategy = stbase.Strategy(None, None)):
        StrategyEntity.__init__(self, strategy)

    def execute(self, code, cycle='1m'):
        """ MACD 买卖策略 """

        stock = stbase.stocks.getTradeObject(code)
        bars = stock.market.getHistoryBars(code,cycle, limit=100)
        close = map(lambda _: _.close, bars)  # 收盘价格列表
        close = np.array(close)
        dif, dea, macd = stalgorithm.MACD(close)
        last = macd[-1]
        # macd 正负值判别决定开仓平仓
