#coding:utf-8

import time,datetime
import os,os.path
import json
import traceback
from threading import Thread,Condition
from Queue import Queue
from collections import OrderedDict

from mantis.fundamental.utils.timeutils import timestamp_current, timestamp_to_str,datetime_to_timestamp,\
    current_datetime_string,current_date_string,TimedTask
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.utils.useful import singleton


from base import *
from tradeobject import *

class ProductConfig(object):
    """产品配置信息"""
    def __init__(self):
        self.broker_id= ''  # 经纪商代码
        self.user_id = ''   # 客户编号
        self.password = ''  # 登录密码
        self.md_addr = ''   # 行情服务器
        self.td_addr = ''   # 交易服务器
        self.product_info = ''  # 产品信息
        self.auth_code = ''     # 认证服务码
        self.others = None      # 附加数据

class Product(object):
    """产品市场"""
    FUTURES = 'futures'
    STOCKS = 'stock'
    def __init__(self,type_):
        self.type_ = type_
        self.market = None  # 行情接口对象
        self.trader = None   # 交易接口对象
        self.conf = ProductConfig()      # 连接信息

    def setupMarket(self,market):
        self.market = market
        market.product = self
        return self

    @property
    def name(self):
        return self.type_

    def setupTrader(self,trader):
        self.trader = trader
        trader.product = self
        return self

    def setup(self,market,trader = None):
        if market:
            self.setupMarket(market)
        if trader:
            self.setupTrader(trader)
        return self

    def setConfig(self,**kwargs):
        """设置配置参数
          如果提供 'file' ,则从配置文件读取，其它参数覆盖已存在的配置项目
          setConfig(broker_id='999',user_id='778261',...)

        """
        if kwargs.has_key('file'):
            pass
        object_assign(self.conf,kwargs)
        return self

    def getConfig(self):
        return self.conf

    def newTradeObject(self,code):
        raise NotImplementedError()

    def getOrNewTradeObject(self, code):
        raise NotImplementedError()

    def open(self):
        if self.market:
            self.market.open()
        if self.trader:
            self.trader.open()

    def close(self):
        if self.market:
            self.market.close()
        if self.trader:
            self.trader.close()

    def getAmountUsable(self):
        return self.trader.getAmountUsable()

    def getAmountAsset(self):
        """现货总资产"""
        return self.trader.getAmountAsset()

    def getPosition(self,code,strategy_id=None):
        """查詢指定合約的持倉記錄"""
        return self.trader.getPosition(code,strategy_id)


class FuturesProduct(Product):
    """期货产品 """
    def __init__(self):
        Product.__init__(self,Product.FUTURES)
        self.trade_objects = OrderedDict()

    def newTradeObject(self,code):
        tradeobj = TradeObject(code,self)
        self.trade_objects[code] = tradeobj
        self.market.initTradeObject(tradeobj)
        return tradeobj

    def getOrNewTradeObject(self,code):
        tradeobj =  self.trade_objects.get(code)
        if not tradeobj:
            tradeobj = self.newTradeObject(code)
        return tradeobj

    def getTradeObject(self,code):
        return self.trade_objects.get(code)

class StocksProduct(Product):
    """股票产品"""
    def __init__(self):
        Product.__init__(self,Product.STOCKS)
        self.stocks = OrderedDict()

    def newTradeObject(self,code):
        stock = TradeObject(code,self)
        self.stocks[code] = stock
        self.market.initTradeObject(stock)
        return stock

    def getOrNewTradeObject(self,code):
        tradeobj =  self.stocks.get(code)
        if not tradeobj:
            tradeobj = self.newTradeObject(code)
        return tradeobj

    def getTradeObject(self,code):
        return self.stocks.get(code)