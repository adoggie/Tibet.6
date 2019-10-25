#coding:utf-8

"""
AMS 策略运行

1. 初始化数据库
  Tradex/AMS/init_accounts.py , init_codes.py
2.  加载策略
  AMS 软件新建策略脚本，添加
    import sys
    import os
    import time
    import threading
    import ctypes

    sys.path.append('F:/Projects/Branches')
    import mantis.sg.fisher.examples.ams.strategy_ams_test2 as module
    from mantis.sg.fisher.ams import Context

    Context().init(Market,Strategy)
    Context().ResTable.OrderItem = OrderItem
    Context().launch(module)
"""

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

# from mantis.sg.fisher.strepo.simple_ma import SimpleMA
# from mantis.sg.fisher.strepo.simple_macd import SimpleMACD
# from mantis.sg.fisher.strepo.simple_bband import SimpleBBand
# from mantis.sg.fisher.strepo.zf_inday import ZFInDay

from mantis.sg.fisher.model import model
from mantis.sg.fisher import stutils

class ASM_Strategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

        self.open_prices = {
            -0.04: {'num': 100, 'times': 1},
            -0.02: {'num': 100, 'times': 1}
        }
        self.cover_prices = {
            0.02: {'num': 100, 'times': 1},
            0.04: {'num': 100, 'times': 1},
        }
        self.open_allow = True
        self.cover_allow = True


    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)
        self.any = dict( inday_buy_count = {},  # 意图控制买卖下单的次数
                        inday_sell_count = {}
                         )
        return self

    def prepared(self):
        delta = datetime.datetime.now() - self.start_time
        return delta.total_seconds() > 5

    def do_zf(self, tick):
        """日内涨跌幅策略
        """

        if not self.prepared():
            print 'System Preparing , Please Wait a while..'
            return

        if not stutils.Stocks.in_trading_time():
            print 'Current is not in Trading Time!'
            return

        # if tick.code != '002517':
        #     return

        code = tick.code
        stock = stbase.stocks.getTradeObject(code)

        # zf = stock.last_price / stock.yd_close - 1
        zf = stock.price.diff_rate

        # strategy_name = 'strategy_inday'
        # st_price = stock.yd_close * (1 + limit)
        # st_price = round(st_price, 2)

        cs = self.get_code_params(tick.code)

        if cs.oc_last != 'open':
            for limit,pp in self.open_prices.items():
                if zf <= limit  :
                    num = pp['num']
                    if stock.price.last < 8 :
                        num = 200

                    pos = self.getPosition(cs.code)
                    if pos.qty_td + num > cs.limit_buy_qty:
                        print code,' open num reached max-limitation!'
                        break

                    st_price = stock.price.sell_1
                    self.logger.takeSignal(stbase.StrategySignal(code, text='strategy_zf_inday, (zf <= limit), '
                                                                            'zf:%s last_price:%s  yd_close_price:%s' %
                                                                            (zf, stock.last_price, stock.yd_close)
                                                                 )
                                           )

                    cs.oc_last = 'open'
                    cs.save()
                    order_req = self.buy(code, st_price, num)
                    break

        if cs.oc_last !='cover':
            for limit,pp in self.cover_prices.items():
                if zf >= limit:
                    num = pp['num']
                    if stock.price.last < 8 :
                        num = 200
                    pos = self.getPosition(cs.code)
                    if pos.qty_yd < num:
                        print code, ' cover num  too less !'
                        break
                    st_price = stock.price.buy_1
                    self.logger.takeSignal(stbase.StrategySignal(code,
                                                                 text='strategy_inday, (zf >= limit), zf:%s last_price:%s  yd_close_price:%s' %
                                                                      (zf, stock.last_price, stock.yd_close)
                                                                 )
                                           )
                    cs.oc_last = 'cover'
                    cs.save()
                    order_req = self.sell(code, st_price, num)
                    break

    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        stock = stbase.stocks.getTradeObject(tick.code)

        # 写入交易股票的当前价格
        cp = model.CodePrice.get(code=tick.code)
        if not cp:
            cp = model.CodePrice()
            cp.code = tick.code
            cs = self.get_code_params(tick.code)
            cp.name = cs.name
        cp.assign(tick.price.dict())
        cp.assign(dict(yd_close=stock.yd_close))

        cp.save()

        # 记录当前股票持仓信息
        cp = model.CodePosition.get(code=tick.code, strategy_id=self.id)
        if not cp:
            cp = model.CodePosition()
        pos = self.getPosition(tick.code)
        cp.assign(pos.dict())
        cp.code = tick.code
        cs = self.get_code_params(tick.code)
        cp.name = cs.name
        cp.strategy_id = self.id
        cp.save()

        stbase.println(tick.code, tick.price.last, tick.price.buy_1, tick.price.sell_1)
        cs = self.get_code_params(tick.code)
        print cs.name, cs.strategy_id, cs.enable, cs.value
        self.do_zf(tick)
        print '-' * 40
        print ''

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
        if bar.cycle != '1m':
            return
        self.exec_boll(bar)

    def exec_boll(self,bar):
        """布林计算"""
        from mantis.sg.fisher.stbase.array import ArrayManager

        ks = self.product.market.getHistoryBars(bar.code, cycle='1m', lasttime= bar.time)
        close = map(lambda _: _.close, ks)
        am = ArrayManager().setCloseArray(close)

        mid = am.ma(20)
        up,down = am.boll(20,2)

        tradeobj = self.product.getTradeObject(bar.code)

        print 'code:{} last_price:{} up:{} mid:{} down:{}'.format(bar.code,tradeobj.last_price,up,mid,down)

        cs  = self.getCodeParams(bar.code)
        if tradeobj.last_price <= down:
            if cs.oc_last != 'open':
                # self.buy(bar.code,tradeobj.last_price,1)
                self.logger.takeSignal(stbase.StrategySignal(code=bar.code,text=u'Boll(Open) last:{} <= down:{}'.format(tradeobj.last_price,down)))

        if tradeobj.last_price >= up:
            if cs.oc_last == 'open':
                self.logger.takeSignal(stbase.StrategySignal(code=bar.code, text=u'Boll(Close) last:{} >= up:{}'.format(
                    tradeobj.last_price, up)))

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
        code = '0600736'
        to = stbase.stocks.getTradeObject(code)
        pos = self.product.getPosition(code)
        # stbase.println(pos.dict())
        print pos
        amount = self.product.getAmountUsable()
        asset = self.product.getAmountAsset()
        print amount ,asset
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

        ks = self.product.market.getHistoryBars(code, cycle='1m')
        close = map(lambda _: _.close, ks)
        print close


    def onPositionChanged(self):
        """持仓或资金变动事件"""
        print 'Postion Changed..'

    def onRtsChanged(self, rts_list):
        print 'RtsChanged ..'


strategy_id  ='AMS_ZF_InDay'
mongodb_host = '192.168.1.252'
data_path = 'z:/ams/zfinday'

def init(context):
    from mantis.sg.fisher.stutils import get_trade_database_name
    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    dbname = get_trade_database_name('AMS')
    paramctrl.open(host=mongodb_host, dbname= dbname)
    # 策略控制器
    stbase.controller.init(data_path)
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender(strategy_id))
    stbase.controller.setParamController(paramctrl)

    stbase.stocks.setup(ams.ASM_StockMarket().init(context), ams.ASM_StockTrader().init(context))
    # stbase.stocks.market.setupRecorder(stbase.MarketFileRecorder(stbase.controller.data_path)) # 安裝行情記錄器
    # stbase.stocks.market.setupRecorder(strecoder.MarketMongoDBRecorder(db_prefix='AMS_Stocks', host='192.168.1.252'))  # 安裝行情記錄器
    strategy = ASM_Strategy(strategy_id,stbase.stocks).init()
    #设置策略日志
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix=dbname,host=mongodb_host))
    stbase.controller.addStrategy(strategy)

    stbase.controller.run()


"""


import sys
import os 
import time
import threading
import ctypes

sys.path.append('F:/Projects/Branches')
import mantis.sg.fisher.examples.ams.strategy_ams_test2 as module
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
