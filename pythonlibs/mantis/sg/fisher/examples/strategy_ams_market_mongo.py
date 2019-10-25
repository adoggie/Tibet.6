#coding:utf-8


import time,datetime
from collections import OrderedDict
from functools import partial
from utils.importutils import import_module
from utils.useful import singleton
import stbase
import ams
import strecoder

class ASM_Strategy(stbase.Strategy):
    # CODES = ['0600000','0600006','0600050','1300025','1300252','1300310']
    CODES = ['0600006','0600050','1300025','1300252','1300310']
    BARS = {'1m': CODES, '5m': CODES, '15m': CODES, '30m': CODES, '60m': CODES, 'd': []}
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)
        return self

    def getSubTickCodes(self):
        return self.CODES

    def getSubBarCodes(self):
        return self.BARS

    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        print tick
        pass

    def onBar(self,bar):
        """
        :param bar: stbase.BarData
        :return:
        """
        print bar
        pass

def init(context):
    stbase.controller.init('z:/ams/fisher')
    stbase.stocks.setup(ams.ASM_StockMarket().init(context), ams.ASM_StockTrader().init(context))
    # stbase.stocks.market.setupRecorder(stbase.MarketFileRecorder(stbase.controller.data_path)) # 安裝行情記錄器
    stbase.stocks.market.setupRecorder(strecoder.MarketMongoDBRecorder(db_prefix='AMS_Stocks',host='192.168.1.252')) # 安裝行情記錄器
    stbase.controller.addStrategy(ASM_Strategy('ASM_Strategy',stbase.stocks).init())
    stbase.controller.run()
    stbase.println("Strategy : Market MongoDB Recorder Started..")

"""

（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000


import sys
import os 
import time
import threading
import ctypes

sys.path.append('F:/Projects/Branches')
import mantis.sg.fisher.strategy_ams_market_mongo as module
from mantis.sg.fisher.ams import Context

Context().init(Market,Strategy)
Context().ResTable.OrderItem = OrderItem
Context().launch(module)

"""
