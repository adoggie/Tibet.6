#coding:utf-8



import json
import numpy as np
import talib as ta

import os,os.path
from mantis.sg.fisher import stbase
import time
import datetime
from mantis.sg.fisher.utils.timeutils import current_datetime_string

import time,datetime
from collections import OrderedDict
from functools import partial

from mantis.sg.fisher.utils.importutils import import_module
from mantis.sg.fisher.utils.useful import singleton

from mantis.sg.fisher import stbase
from mantis.sg.fisher import ams
from mantis.sg.fisher import strecoder
from mantis.sg.fisher import stsim
from mantis.sg.fisher import stgenerator

from mantis.sg.fisher.strepo.simple_ma import SimpleMA
from mantis.sg.fisher.strepo.simple_macd import SimpleMACD
from mantis.sg.fisher.strepo.simple_bband import SimpleBBand
from mantis.sg.fisher.strepo.zf_inday import ZFInDay

class ASM_Strategy(stbase.Strategy):
    CODES = ['0600000']
    CODES = ['0600834']
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
        # stbase.println(tick.code,tick.price.last,tick.price.buy_1,tick.price.sell_1)
        pass
        # print tick.json()
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
        stbase.println(bar.code,bar.cycle,bar.close,bar.vol)
        # print bar.json()
        # if bar.cycle == '5m':
        #     self.sma.execute(bar.code,bar.cycle)

    def onTimer(self,timer):
        print 'ontimer..'
        # timer.start()
        code = '0600000'
        obj = stbase.stocks.getTradeObject(code)
        # print obj.last_price

        # print obj.price.dict()
        # print 'on buy() or sell() ..'
        # self.buy('0600000',obj.price.sell_1,100)
        # self.sell('0600000',obj.price.buy_1,100)

        # 以最低价下委托买入
        for _ in range(1):
            stbase.println('try buy({})..'.format(obj.min_price))
            self.buy(code,obj.min_price,100)
            #
            # stbase.println('try sell({})..'.format(30))
            # self.sell(code, obj.max_price, 100)
            time.sleep(1)


    def start(self):
        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")

        code = '0600000'
        to = stbase.stocks.getTradeObject(code)
        pos = self.product.getPosition(code)
        stbase.println(pos.dict())
        amount = self.product.getAmountUsable()
        asset = self.product.getAmountAsset()

        # stbase.println('amount:{}'.format(amount) )
        # stbase.println('asset:{}'.format(asset)  )

        # self.startTimer(timeout=5)
        # return

        # 打印持仓信息
        # pos_list = self.getPosition()
        # for pos in pos_list:
        #     stbase.println( 'code:%s , yd_qty:%s'%(pos.code,pos.qty_yd))
        #
        # 打印委托记录（在委托中..)
        # orders = self.getOrders(order_id=111)
        # orders = self.getOrders()
        # for order in orders:
        #     stbase.println( order )
        #     self.cancelOrder(order.order_id)

        # self.cancelOrder(390941)

    def onPositionChanged(self):
        """持仓或资金变动事件"""
        print 'Postion Changed..'

    def onRtsChanged(self, rts_list):
        print 'RtsChanged ..'



def init(context):
    stbase.controller.init('z:/ams/fisher')
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('ASM_Strategy_Test2'))

    stbase.stocks.setup(ams.ASM_StockMarket().init(context), ams.ASM_StockTrader().init(context))
    # stbase.stocks.market.setupRecorder(stbase.MarketFileRecorder(stbase.controller.data_path)) # 安裝行情記錄器
    # stbase.stocks.market.setupRecorder(strecoder.MarketMongoDBRecorder(db_prefix='AMS_Stocks', host='192.168.1.252'))  # 安裝行情記錄器
    strategy = ASM_Strategy('ASM_Strategy_Test1',stbase.stocks).init()
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

期货 00007604 /203669/xyzq601377

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000

AMS 另一套账号
===========
sfhj000 xyzq601377
资金账号：20004038
密码：112233

"""
