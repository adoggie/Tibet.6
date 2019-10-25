#coding:utf-8


"""
回测期货历史数据

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
from pymongo import MongoClient


from mantis.sg.fisher.utils.importutils import import_module
from mantis.sg.fisher.utils.useful import singleton
from mantis.fundamental.utils.timeutils import current_date_string

from mantis.sg.fisher import stbase
from mantis.sg.fisher import ams
from mantis.sg.fisher import strecoder
from mantis.sg.fisher import stsim
from mantis.sg.fisher import stgenerator

from mantis.sg.fisher.stbase.base import BarDataEndFlag

from  mantis.sg.fisher.strepo import ZFInDay
from mantis.sg.fisher.model import model
from mantis.sg.fisher.ctp.backtest import CtpMarketBarBackTest
from mantis.sg.fisher import stutils

from mantis.sg.fisher.stbase.array import ArrayManager
import config

SYMBOL = u'CF'

OPENCLOSE_FEE = 10 #开平一次手续费

SAMPLE_DATE_RANGE =('2015-6-18 9:0' ,'2019-6-19 15:0')

class MyStrategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

        self.product_close_array ={} # 收盘价array

        self.direction = 'idle' # [idle,long,short]
        self.position = 0 # 持仓数量
        self.order_bar = None # 委托下单 的k线
        self.open_days = 0 # 委托下单开始的交易日
        self.num = 1
        self.amount = 1000*1000 # 100w
        self.balance = self.amount
        self.fee_ratio = 0.01    # 手续费率
        self.margin_ratio = 0.07 # 保证金率
        self.margin_amount = 0   # 保证金总额

        self.trade_table = [] # OrderedDict()
        self.last_bar = None

        self.open_times = 0  # 累计开仓次数

        self.amount_init = 0 # 初始资金
        self.amount = 0

        self.open_price = 0  # 开仓价格

        self.bar_count = 0


    def amountUsable(self):
        """可用资金"""
        return self.amount - 0

    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)

        return self

    def getSubTickCodes(self):
        return stbase.Strategy.getSubTickCodes(self)

    def getSubBarCodes(self):
        # return stbase.Strategy.getSubBarCodes(self)
        return {'d':[SYMBOL]}

    def prepared(self):
        delta = datetime.datetime.now() - self.start_time
        return delta.total_seconds() > 5


    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        # return


    def onBar(self,bar):
        """
        :param bar: stbase.BarData
        :return:
        bar.cycle : ['1m','5m','15m','30m','60m','d','w','m','q','y']
        bar.code :
        bar.trade_object :
        .open .close .high .low .vol .amount .time
        """

        if isinstance(bar,BarDataEndFlag):
            self.onReachEnd()
            return

        self.bar_count+=1

        self.last_bar = bar
        print 'SYM：',bar.symbol, 'Time:',bar.time, 'High:',bar.high,'Low:',bar.low,'Open:',bar.open,'Close:',bar.close
        self.exec_wr_atr(bar)
        # if bar.cycle !='1m':
        #     return
        # return
        # am = self.product_close_array.get( bar.code)

        # if not am:
        # if True:
        #     # ----------------------------------
        #     # 初始化制定商品的历史k线缓存100 条
        #     ks = self.product.market.getHistoryBars(bar.code, cycle='d',lasttime= bar.time)
        #     am = ArrayManager()  # .setCloseArray(close)
        #     for k in ks:
        #         am.updateBar(k)
        #     self.product_close_array[bar.code] = am
        #
        # am.updateBar(bar)

        # self.exec_boll(bar,am)
        # if bar.cycle == '5m':
        #     self.sma.execute(bar.code,bar.cycle)

    def onReachEnd(self):
        self.tradeFinished()
        print 'Reach End . Ready To Stop ..'

        self.reportView()

        stbase.controller.stop()

    def tradeFinished(self):
        # 完成最后平仓
        if self.direction == 'idle':
            return
        self.position -=1

        # if self.direction ==  'long':


    def exec_wr_atr(self,bar):
        """策略"""
        STOP_WIN = 23  # 止盈止损 窗口日
        STOP_WIN_MIN = 14

        N = 1
        TIMEPERIOD = 24

        # 当前bar不参与线性拟合
        # ks = self.product.market.getHistoryBars(bar.code, cycle='d', lasttime=bar.time - datetime.timedelta(days=1) , limit=TIMEPERIOD*2)
        ks = self.product.market.getHistoryBars(bar.code, cycle='d', lasttime=bar.time , limit=TIMEPERIOD*2)
        if len(ks)< TIMEPERIOD +1 :
            print 'Stuff Me More Data..'
            return

        if self.direction !='idle':
            self.open_days+=1

        a,b,c = ks[-3:]
        # c 不参与计算
        ks = ks[:-1]

        high = map(lambda _: _.high, ks)
        low = map(lambda _: _.low, ks)
        close = map(lambda _: _.close, ks)
        high = np.array(high, dtype=np.double)
        low = np.array(low, dtype=np.double)
        close = np.array(close, dtype=np.double)
        mid =(high + low + close ) /3.
        # print mid
        mid = ta.MA(mid, TIMEPERIOD)
        # print mid
        atr = ta.ATR( high, low, close, TIMEPERIOD)
        up = mid + atr *N
        down = mid - atr *N

        # print 'up:',up[-1],' down:', down[-1], ' mid:',mid[-1]

        td = bar
        # yd = ks[-1]

        v1  = (b.high + b.low + b.close ) / 3.
        v2  = (a.high + a.low + a.close ) / 3.
        close = b.close

        # LONG enter
        if self.direction in ('idle','short') and close > up[-1] and v1 > v2:
            """
            1.空仓或空头
            2. close > up 
            3. td[ (high+low+close)/3] > yd [ (high+low+close)/3 ]
            """
            if self.direction == 'short':
                self.position -=1 # 平空仓
                trade = dict(datetime=str(td.time), open=td.open, close=td.close, direction='short', oc='close',
                             price=td.open, num=1)

                self.trade_table.append({'marks': '-- OC:close ,  From short To long --'})
                self.trade_table.append(trade)

                self.amount += self.open_price - td.open
                self.open_price = 0


            open = td.open # 开场价格开仓
            self.position +=1 # 下一手
            self.direction = 'long'
            trade = dict(datetime= str(td.time), open=td.open, close = td.close, direction = 'long',oc='open',price = td.open, num = 1 )
            self.trade_table.append( trade )
            self.order_bar = bar

            self.open_days = 1

            self.open_times +=1

            self.open_price = td.open
            return

        # SHORT enter
        if self.direction in  ('idle','long') and close < down[-1] and v1 < v2:
            """
            1.空仓或多头（反手操作：先平再开) 
            2. close < down 
            3. td[ (high+low+close)/3] < yd [ (high+low+close)/3 ]
            """
            if self.direction == 'long':
                # do reverse 平仓再反向开仓
                self.position -= 1  # 下一手
                self.trade_table.append({'marks': '-- OC:close ,  From long To short --'})
                trade = dict(datetime=str(td.time), open=td.open, close=td.close, direction='long', oc='close', price=td.open, num=1)
                self.trade_table.append(trade)

                self.amount += td.open - self.open_price
                self.open_price = 0

            open = td.open # 开场价格开仓
            self.position +=1 # 下一手
            self.direction = 'short'
            trade = dict(datetime= str(td.time), open=td.open, close = td.close, direction = 'short',oc='open',price = td.open, num = 1 )
            self.trade_table.append( trade )
            self.order_bar = bar
            self.open_days = 1

            self.open_times += 1

            self.open_price = td.open
            return

        # Leave 离场 zhi ying , zhi shun
        """止盈止损点触发离场
        计算：
        N = 100 日
        1. b日之前的R日的收盘均价 sma([b-n,b]/close) ， 与b日的收盘价比较
        2. 持仓的窗口参数 W ,  R = (N - W )  ( R >= 10 )  已开仓到b日的天数
              
        """

        if self.direction != 'idle': # 非空仓
            R = STOP_WIN - self.open_days
            if R < STOP_WIN_MIN:
                R = STOP_WIN_MIN
            if self.direction in ('long','short'):
                ks = self.product.market.getHistoryBars(bar.code, cycle='d', lasttime=b.time, limit=R*2)
                stopclose = map(lambda _: _.close, ks)
                stopclose = np.array(stopclose, dtype=np.double)
                stopclose = ta.MA(stopclose, R)
                stopclose = stopclose[-1]

            if self.direction == 'long':
                if b.close < stopclose : # 昨日收盘价 < R 日收盘均价 ， 平多
                    self.position -= 1  # 下一手
                    trade = dict(datetime=str(td.time), open=td.open, close=b.close, direction='long', oc='close',
                                 price=td.open, num=1, stopclose=stopclose, open_days=self.open_days, r = R)
                    self.trade_table.append(trade)
                    self.open_days = 0
                    self.direction = 'idle'

                    self.amount += td.open - self.open_price

                    self.open_price = 0

            elif self.direction == 'short': # 平空
                if b.close > stopclose:
                    self.position -= 1  # 平空仓
                    trade = dict(datetime=str(td.time), open=td.open, close=b.close, direction='short', oc='close',
                                 price=td.open, num=1, stopclose = stopclose, open_days=self.open_days, r =R)
                    self.trade_table.append(trade)
                    self.open_days = 0
                    self.direction = 'idle'

                    self.amount += self.open_price - td.open

                    self.open_price = 0

    def reportView(self):
        """输入运行报告"""
        idx = 1
        fp = open('running_report.txt','w')

        # self.trade_table.append(dict(marks='\n'+'='*20 + '\n'))
        # self.trade_table.append(dict(marks='open_times:' + str(self.open_times)))

        for tr in self.trade_table:
            if tr.get('marks'):
                text = tr.get('marks')
            else:
                text = "{:0>3d} time:{} direction:{} oc:{} price:{} close:{} ".format(idx,
                                                                            tr['datetime'],tr['direction'],tr['oc'],tr['price'],
                                                                            tr['close'] )
                if tr.get('stopclose'):
                    text = text + " " + "stop_close:" + str( round(tr.get('stopclose'),2))
                if tr.get('open_days',0):
                    text = text + " open_days:" + str(tr.get('open_days'))

                if tr.get('r'):
                    text += ' R:' + str(tr.get('r'))
                idx +=1

            self.writeView(text,fp)
            # fp.write(text+'\n')
            # print text


        self.writeView('',fp)
        self.writeView( '='*40  , fp)
        self.writeView('',fp)
        self.writeView(u'开仓次数:' + str(self.open_times) ,fp)
        fee = self.open_times * OPENCLOSE_FEE
        self.writeView(u'手续费:' + str(fee),fp)
        self.writeView(u'盈亏:' + str(self.amount - fee ),fp)
        self.writeView(u'样本周期:' + str(SAMPLE_DATE_RANGE),fp)
        self.writeView(u'样本数量:' + str(self.bar_count),fp)
        self.writeView(u'样本单位:' + str('D'),fp)

        fp.close()

    def writeView(self,text,fp,newline=True ):
        print text
        text = text.encode('utf-8')
        fp.write(text)
        if newline:
            fp.write('\n')



    def exec_boll(self,bar,am):
        """布林计算"""

        ks = self.product.market.getHistoryBars(bar.code, cycle='1m', lasttime= bar.time)
        close = map(lambda _: _.close, ks)
        am = ArrayManager().setCloseArray(close)

        mid = am.ma(20)
        up,down = am.boll(20,2)

        tradeobj = self.product.getTradeObject(bar.code)
        last_price = close[-1]
        # print 'code:{} last_price:{} up:{} mid:{} down:{}'.format(bar.code,last_price,up,mid,down)

        cs  = self.getCodeParams(bar.code)

        if last_price <= down:
            if cs.oc_last != 'open':  # 下穿
                # self.buy(bar.code,tradeobj.last_price,1)
                print '>> boll cross down'
                print bar.time,'code:{} last_price:{} up:{} mid:{} down:{}'.format(bar.code, last_price, up, mid, down)
                # self.logger.takeSignal(stbase.StrategySignal(code=bar.code,text=u'Boll(Open) last:{} <= down:{}'.format(last_price,down)))

        if last_price >= up:
            if cs.oc_last == 'open':    # 上传
                print '>> boll cross up'
                print bar.time,'code:{} last_price:{} up:{} mid:{} down:{}'.format(bar.code, last_price, up, mid, down)
                # self.logger.takeSignal(stbase.StrategySignal(code=bar.code, text=u'Boll(Close) last:{} >= up:{}'.format(last_price, up)))

    def onTimer(self,timer):
        print 'ontimer..'
        # timer.start()
        codes = self.get_codes()
        obj = stbase.controller.futures.getTradeObject( codes[0].code )


    def start(self):
        self.set_params(run=self.Runnable.STOP,start='false')  # 停止
        codes =  self.get_codes()
        for code in codes:
            self.setCodeParams(code.code,open_allow=True,cover_allow=True)
            print code.code
        # self.startTimer(self.limit_buy,timeout=2)

        self.subBar(SYMBOL, '1m')     # 手动订阅指定的合约k线，一遍得到k线播放事件

        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")



strategy_id  ='EXPCTP_BACKTEST'
mongodb_host,mongodb_port = config.STRATEGY_SERVER

data_path = './ctp_zsqh-backtest'
dbname = config.STRATEGY_DB_NAME
quotas_db_conn = MongoClient(config.QUOTES_DB_SERVER[0],config.QUOTES_DB_SERVER[1]) # 历史k线数据库

def main():
    # from mantis.sg.fisher.stutils import get_trade_database_name
    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    paramctrl.open(host= mongodb_host,port= mongodb_port,dbname= dbname)
    # 策略控制器
    stbase.controller.init(data_path)
    # 添加运行日志处理
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('CTP'))
    stbase.controller.setParamController(paramctrl)

    param = paramctrl.get(strategy_id)                  # 读取指定策略id的参数
    # conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

    # 初始化行情对象
    params = dict(db_conn= quotas_db_conn ,cycle='d',symbol=SYMBOL,
                  # start='2015-6-18 9:0' , end='2019-6-19 15:0',freq=0,wait=2)
                  start=SAMPLE_DATE_RANGE[0] , end=SAMPLE_DATE_RANGE[1],freq=0,wait=2)
    # params.update( conn_url.dict() )
    market = CtpMarketBarBackTest().init(**params)      # 配置历史行情记录加载器
    # 装备行情对象到股票产品
    stbase.controller.futures.setupMarket(market)
    # 初始化交易对象
    # trader = CtpTrader().init(**conn_url.dict())
    # stbase.controller.futures.setupTrader(trader)

    # 初始化策略对象
    strategy = MyStrategy(strategy_id,stbase.controller.futures).init()
    #设置策略日志对象
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix= dbname,host=mongodb_host,port=mongodb_port))
    # 添加策略到 控制器
    stbase.controller.addStrategy(strategy)
    # 控制器运行
    stbase.controller.run().waitForShutdown() # 开始运行 ，加载k线数据

if __name__ == '__main__':
    main()

"""
mnogodb query statements
----------------------
db.getCollection('AJ_Test1_20190426').find({event:{$in:['order','order_cancel']}},{order_id:1,direction:1,code:1,price:1,oc:1,time:1,quantity:1,_id:0,event:1}).sort({time:-1})

"""