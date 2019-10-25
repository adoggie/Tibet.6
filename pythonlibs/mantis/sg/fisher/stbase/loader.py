#coding:utf-8

"""
策略运行加载器类定义
"""

class StrategyLoader(object):
    def __init__(self):
        self.cfgs = {}
        self.strategy = None

    def init(self,**kwargs):
        self.cfgs.update(**kwargs)

    def getTradeObject(self,bar):
        raise NotImplementedError
