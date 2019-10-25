#coding:utf-8

"""
历史数据回测运行策略
"""

import json
import numpy as np
import talib as ta

import os,os.path

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

# from mantis.sg.fisher.strepo.simple_ma import SimpleMA
# from mantis.sg.fisher.strepo.simple_macd import SimpleMACD
# from mantis.sg.fisher.strepo.simple_bband import SimpleBBand
# from mantis.sg.fisher.strepo.zf_inday import ZFInDay

from mantis.sg.fisher.strepo.base import  StrategyEntity

CODE='1300252'

class ZFInDay(StrategyEntity):
    def __init__(self, strategy=stbase.Strategy(None, None)):
        StrategyEntity.__init__(self, strategy)

    def execute(self, code, num=100, limit=0.01):
        """日内涨跌幅策略
        @:param code: 股票代码
        @:param num ：买卖数量
        @:param limit: 价格浮动限

        当日仅仅允许买卖各触发一次

        """
        stock = stbase.stocks.getTradeObject(code)

        # zf = stock.last_price / stock.yd_close - 1
        zf = stock.price.diff_rate

        # strategy_name = 'strategy_inday'
        # st_price = stock.yd_close * (1 + limit)
        # st_price = round(st_price, 2)

        if zf <= -limit  :
            st_price = stock.price.sell_1
            # self.logger.takeSignal(stbase.StrategySignal(code, text='strategy_zf_inday, (zf <= -limit), '
            #                                                         'zf:%s last_price:%s  yd_close_price:%s' %
            #                                                         (zf, stock.last_price, stock.yd_close)
            #                                              )
            #                        )
            # 跌幅过限
            amount = self.st.product.getAmountUsable()
            # pos_sum = stock.pos.net_total
            pos = self.st.product.getPosition(code)
            if not pos:
                self.logger.debug('yd pos is 0. Exit..')
                stbase.controller.stop()
                return
            #
            if pos.cost_amount <= amount * 0.1 and not self.st.any.get('buy_order_req'):
                """持仓资金占总资金 <= 10% """
                self.logger.debug('do buy: {} ,{}, {}'.format(code, st_price, num),zf=zf)
                order_req = self.st.buy(code, st_price, num)
                self.st.any['buy_order_req'] = order_req
                self.st.any['current_order_req'] = order_req
                self.st.any['sell_order_req'] = None

        elif zf >= limit:
            """ """
            st_price = stock.price.buy_1
            # self.logger.takeSignal(stbase.StrategySignal(code,
            #                                              text='strategy_inday, (zf >= limit), zf:%s last_price:%s  yd_close_price:%s' %
            #                                                   (zf, stock.last_price, stock.yd_close)
            #                                              )
            #                        )

            pos = self.st.product.getPosition(code)
            if not pos:
                self.logger.debug('yd pos is 0. Exit..')
                stbase.controller.stop()
                return

            if pos.qty_yd >= num and not self.st.any.get('sell_order_req'):
                self.logger.debug('do sell: {} ,{}, {}'.format(code, st_price, num))
                order_req = self.st.sell(code, st_price, num)
                self.st.any['sell_order_req'] = order_req
                self.st.any['current_order_req'] = order_req
                self.st.any['buy_order_req'] = None

        # if self.st.any.get('current_order_req'):
        #     order = None
        #     order_req = self.st.any.get('current_order_req')
        #     self.logger.debug('query order:', order_req.order_id)
        #     # orders = Strategy.GetOrdersByOrigSerialNo(current_order_req.order_id)
        #     orders = self.st.getOrders(order_id=order_req.order_id)
        #     self.logger.debug('orders size:', len(orders))
        #
        #     if orders:
        #         order = orders[0]
        #     if order:
        #         self.logger.debug('knockqty:', order.qty_filled)
        #         if order.qty_filled >= order_req.min_knock_num_rate * order_req.num:
        #             if order_req.direction == stbase.Constants.Buy:
        #                 self.st.any['sell_order_req'] = None  # 允许开卖
        #             if order_req.direction == stbase.Constants.Sell:
        #                 self.st.any['buy_order_req'] = None
        #
        #             self.st.any['current_order_req'] = None
        #             # count += 1
        #



class ASM_Strategy(stbase.Strategy):
    CODES = ['0600000']
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

        # self.sma = SimpleMA(self)
        # self.macd = SimpleMACD(self)
        # self.bband = SimpleBBand(self)
        self.zf = ZFInDay(self)


    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)
        self.any = dict( inday_buy_count = {},  # 意图控制买卖下单的次数
                        inday_sell_count = {}
                         )
        return self

    def getSubTickCodes(self):
        return [CODE,]

    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        # print tick.price.dict()
        # print 'code:',tick.code
        self.zf.execute(tick.code)


    def onBar(self,bar):
        """
        :param bar: stbase.BarData
        :return:
        bar.cycle : ['1m','5m','15m','30m','60m','d','w','m','q','y']
        bar.code :
        bar.trade_object :
        .open .close .high .low .vol .amount .time
        """
        # print bar.json()
        # if bar.cycle == '5m':
        #     self.sma.execute(bar.code,bar.cycle)
        pass

    def onTimer(self,timer):
        timer.start()

    def start(self):
        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")

        code = CODE
        to = stbase.stocks.getTradeObject(code)
        pos = self.product.getPosition(code)
        stbase.println(pos.dict())
        amount = self.product.getAmountUsable()
        asset = self.product.getAmountAsset()
        stbase.println(amount)
        stbase.println(asset)




def backtest():
    """历史行情回测"""
    stbase.controller.init('z:/ams/backtest')
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('BackTest_1'))
    # generator = stgenerator.MarketGeneratorFileTDX().init(src_file= os.path.join(stbase.controller.getDataPath(),'tdx.txt'))
    # generator = stgenerator.MarketGeneratorTushare().init(code='600000',start='2018-10-04',end='2019-02-01',ktype='5')

    strategy = ASM_Strategy('ASM_Strategy_Test1', stbase.stocks).init()
    # 设置策略日志
    strategy.getLogger().addAppender(
        strecoder.StragetyLoggerMongoDBAppender(db_prefix='AMS_Stocks', host='192.168.1.252'))
    stbase.controller.addStrategy(strategy)
    # 创建模拟行情发生器对象
    generator = stgenerator.MarketGeneratorMongoDBBar().init(code=CODE,
                                                             # ktype='5m',
                                                             # play_start='20190311 09:20:00',
                                                             # play_end='20190311 15:10:00',
                                                             host='192.168.1.252',
                                                             db='AMS_Stocks_Ticks',
                                                             async_send = False
                                                             # db='AMS_Stocks_Bars',
                                                             )
    generator.onEnd = stbase.controller.stop # 行情播报结束

    stbase.stocks.setup(stsim.BackStockMarket().setupGenerator(generator), stsim.BackStockTrader())
    stbase.controller.run()
    generator.open()
    # stbase.controller.waitForShutdown()

if __name__=='__main__':
    backtest()

"""

import sys
import os
import time
import threading
import ctypes

sys.path.append('F:/Projects/Branches')
from mantis.sg.fisher.ams import Context
Context().init(Market,Strategy)
Context().ResTable.OrderItem = OrderItem
Context().launch('mantis.sg.fisher.strategy_ams_sample')

（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000

"""
