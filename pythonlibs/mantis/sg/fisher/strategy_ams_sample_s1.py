#coding:utf-8



import json
import numpy as np
import talib as ta

import os,os.path
import stbase
import time
import datetime
from utils.timeutils import current_datetime_string

import time,datetime
from collections import OrderedDict
from functools import partial
from utils.importutils import import_module
from utils.useful import singleton

import stbase
import ams
import strecoder
import stsim
import stgenerator

from strepo.simple_ma import SimpleMA
from strepo.simple_macd import SimpleMACD
from strepo.simple_bband import SimpleBBand
from strepo.zf_inday import ZFInDay

class ASM_Strategy(stbase.Strategy):
    CODES = ['0600000']
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

        self.sma = SimpleMA(self)
        self.macd = SimpleMACD(self)
        self.bband = SimpleBBand(self)
        self.zf = ZFInDay(self)


    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)
        self.any = dict( inday_buy_count = {},  # 意图控制买卖下单的次数
                        inday_sell_count = {}
                         )
        return self

    def getSubTickCodes(self):
        return self.CODES

    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        # pass
        print tick.json()
        # print tick.trade_object.limit_price,tick.trade_object.last_price
        # print tick.trade_object.code

        base_price = 0
        # self.strategy_inday(tick.trade_object.code, 100, 0.001)
        # to = stbase.stocks.getTradeObject(tick.trade_object.code)
        # print to

        # self.strategy_inday(tick.trade_object.code, 100, 0.001)

    def onBar(self,bar):
        """
        :param bar: stbase.BarData
        :return:
        bar.cycle : ['1m','5m','15m','30m','60m','d','w','m','q','y']
        bar.code :
        bar.trade_object :
        .open .close .high .low .vol .amount .time
        """
        print bar.json()
        # if bar.cycle == '5m':
        #     self.sma.execute(bar.code,bar.cycle)

    def onTimer(self,timer):
        timer.start()

    def start(self):
        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")

        code = '0600000'
        to = stbase.stocks.getTradeObject(code)
        pos = self.product.getPosition(code)
        stbase.println(pos.dict())
        amount = self.product.getAmountUsable()
        asset = self.product.getAmountAsset()
        stbase.println('amount:{}'.format(amount) )
        stbase.println('asset:{}'.format(asset)  )



def init(context):
    stbase.controller.init('z:/ams/fisher')
    stbase.stocks.setup(ams.ASM_StockMarket().init(context), ams.ASM_StockTrader().init(context))
    # stbase.stocks.market.setupRecorder(stbase.MarketFileRecorder(stbase.controller.data_path)) # 安裝行情記錄器
    # stbase.stocks.market.setupRecorder(strecoder.MarketMongoDBRecorder(db_prefix='AMS_Stocks', host='192.168.1.252'))  # 安裝行情記錄器
    strategy = ASM_Strategy('ASM_Strategy_s1',stbase.stocks).init()
    #设置策略日志
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix='AMS_Stocks',host='192.168.1.252'))


    stbase.controller.addStrategy(strategy)
    stbase.controller.run()

def backtest():
    """历史行情回测"""
    stbase.controller.init('z:/ams/backtest')
    #
    generator = stgenerator.MarketGeneratorTDXBar().init(src_file= os.path.join(stbase.controller.getDataPath(),'tdx.txt'))

    stbase.stocks.setup(stsim.BackStockMarket().setupGenerator(generator), stsim.BackStockTrader())

    strategy = ASM_Strategy('ASM_Strategy_s1', stbase.stocks).init()
    # 设置策略日志
    strategy.getLogger().addAppender(
        strecoder.StragetyLoggerMongoDBAppender(db_prefix='AMS_Stocks', host='192.168.1.252'))
    stbase.controller.addStrategy(strategy)
    stbase.controller.run()

if __name__=='__main__':
    backtest()

"""


import sys
import os 
import time
import threading
import ctypes

sys.path.append('F:/Projects/Branches')
import mantis.sg.fisher.strategy_ams_sample_s1 as module
from mantis.sg.fisher.ams import Context

Context().init(Market,Strategy)
Context().ResTable.OrderItem = OrderItem
Context().launch(module)



（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000

"""
