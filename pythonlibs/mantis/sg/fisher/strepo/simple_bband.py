#coding:utf-8

"""
bollin band.py

不林带
"""

import numpy as np
import talib as ta
from mantis.sg.fisher import stbase
from mantis.sg.fisher import stalgorithm
from base import StrategyEntity


class SimpleBBand(StrategyEntity):
    def __init__(self,strategy = stbase.Strategy(None, None)):
        StrategyEntity.__init__(self, strategy)

    def strategy_bband(self,code,cycle='1m'):
        """布林带 买卖策略"""
        pass
