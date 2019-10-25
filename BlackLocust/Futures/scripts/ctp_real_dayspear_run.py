#coding:utf-8


"""
日k基线的期货策略运行
ctp_real_dayspear_run.py

1.日收盘拉取当日价格开高低收
2.生成开盘之后的交易策略
3.开盘即刻成交，并停止策略运行，不成交就无动作

程序启动判别是否开平仓
1. 启动时间是否在交易时间段
2. 当日是否已执行


python ctp_real_dayspear.py strategy_id run
 - strategy_id  策略编号，与ctp_init_codes.py 对应
 - run 开启下单委托 ，未提供则仅仅输出策略运算信号 "sig-strategy_id-ymd.txt'

查看 信号文件
 cat *.txt | cat -n

"""
import json
import traceback
import numpy as np
import talib as ta
import pandas as pd
from dateutil.parser import parse

import os,os.path,sys
from mantis.sg.fisher import stbase
import datetime
from mantis.sg.fisher.utils.timeutils import current_datetime_string

import time,datetime
from collections import OrderedDict
from functools import partial
from pymongo import MongoClient

import matplotlib.pyplot as plt
from plot_utils import export_png_base64
#---- splitter ----

from mantis.sg.fisher.utils.importutils import import_module
from mantis.sg.fisher.utils.useful import singleton ,object_assign
from mantis.fundamental.utils.timeutils import current_date_string
from mantis.fundamental.redis.broker import MessageBroker

import mantis.sg.fisher.model as model
from mantis.sg.fisher import stbase
from mantis.sg.fisher import strecoder
from mantis.sg.fisher.stbase.base import BarDataEndFlag
from mantis.sg.fisher.ctp.backtest import CtpMarketBarBackTest
from mantis.sg.fisher.ctp.ctp import CtpMarket,CtpTrader
# from mantis.fundamental.utils.file import file_lock

import config

PWD = os.path.dirname( os.path.abspath(__file__) )



strategy_id  ='ctp_day_spear'
mongodb_host,mongodb_port = config.STRATEGY_SERVER

data_path = './data-{}'.format(strategy_id)
dbname = config.STRATEGY_DB_NAME
quotas_db_conn = MongoClient(config.QUOTES_DB_SERVER[0],config.QUOTES_DB_SERVER[1]) # 历史k线数据库


SYMBOL = u'CF'
DATASET = u'CF' #数据集
INDEX = ''


class MyStrategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)
        self.bar_list = []  # 缓存所有进入的bar记录
        self.param_table ={}
        self.reset()

        self.cs = None # 当前运行商品代码信息  see `model.CodeSettings`
        self.last_tick = None
        self.code = '' # 当前商品代码
        self.order_enable = False #是否允许交易下单
        self.sig_log = None
        self.sig_params = OrderedDict()
        self.plot_data = OrderedDict()




    def reset(self):
        pass 
        # self.direction = 'idle' # [idle,long,short]
        #
        # self.order_bar = None # 委托下单 的k线
        # self.open_days = 0 # 委托下单开始的交易日
        # self.num = 1
        #
        # self.trade_table = [] # OrderedDict()
        # self.last_bar = None
        #
        # self.open_times = 0  # 累计开仓次数
        # self.close_times = 0  # 累计平仓次数
        #
        # # self.amount_init = INIT_FUNDS # 初始资金
        # self.amount = self.amount_init  # 100w
        # self.margin_amount = 0 # 当前保证金数

        # self.open_price = 0  # 开仓价格
        # self.position = 0  # 持仓数量

        # self.bar_count = 0
        
        # self.fee_amount = 0 # 手续费总数
        #
        # self.output_file = None
        # self.output_detail = './detail'
        # if not os.path.exists(self.output_detail):
        #     os.mkdir(self.output_detail)
        #
        # self.fee = 0        # 当日交易手续费累计
        # self.fee_in_day = 0 # 当日手续费
        # self.net_list = [] # 净值序列 [k:v,..] , [{bar:net},...]


    # def amountUsable(self):
    #     """可用资金"""
    #     return self.amount - 0

    def init(self,*args,**kwargs):
        self.init_channel_pub()
        stbase.Strategy.init(self,*args,**kwargs)
        return self

    def stop(self):
        stbase.Strategy.stop(self)
        if self.broker:
            self.broker.close()
        self.log_print(message="Strategy Stopped.")

    def init_channel_pub(self):

        self.broker = MessageBroker()
        host, port, db, passwd = config.MD_BROKER.split(':')
        self.broker.init(dict(host=host, port=port, db=db, password=passwd))
        self.broker.open()

        channelname = 'strategy_logs_message${}'.format(self.id)
        self.pub_log_message = self.broker.createPubsubChannel(channelname)
        self.pub_log_message.open()

        channelname = 'strategy_logs_trade${}'.format(self.id)
        self.pub_log_trade = self.broker.createPubsubChannel(channelname)
        self.pub_log_trade.open()

    def prepared(self):
        delta = datetime.datetime.now() - self.start_time
        return delta.total_seconds() > 5


    def onTick(self,tick):
        """
        开盘行情接收触发策略计算
        """


        cs = self.get_code_params(self.code)
        self.cs = cs

        # if not self.last_tick:
        #     self.order_open(tick.price.last, stbase.Constants.Short)
        #     stbase.controller.stop()
        self.last_tick = tick



        # print 'max order num:',self.get_max_order_num(tick.price.last)



    def onBar(self,bar):
        pass

    def get_amount(self):
        """查询可交易资金额"""
        amount = 0
        stat = self.getAccountStat()
        if stat:
            amount =  stat.Available
        return amount

    def get_position(self,direction):
        """查询持仓"""
        rs = self.getPosition(self.code,self.id,direction)
        # rs = self.getPosition('AP910',self.id,direction)
        pos = 0
        if rs:
            # pos = rs[0].YdPosition
            pos = rs[0].Position
        return pos

    def get_max_order_num(self,price):
        """计算可用下单委托数量"""
        return 1

        usable = self.get_amount() * self.cs.MAX_MARGIN_AMOUNT
        fee = price * self.cs.MARGIN_RATIO
        num = usable // fee // self.cs.LOT_PER_UNIT
        return num

    def get_open_days(self,ks):
        """查询持仓天数 """
        open_days = 0
        if self.cs.direction == stbase.Constants.Idle:
            return open_days

        open_date = self.cs.open_date
        for idx,k in enumerate(ks) :
            if k.datetime == open_date:
                open_days = len(ks) - idx
                break
        return open_days


    def _order_open(self,price,direction,vol=1):
        """开仓"""

        cs = self.cs
        if not vol:
            vol = self.get_max_order_num(price) # 计算开仓数量

        if direction == stbase.Constants.Long:  #  买开
            price = self.last_tick.price.last + 2
            self.buy(self.code, price, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.LimitPrice,exchange_id=cs.exchange_id,
                    cc = stbase.futures.Constants.ContingentConditionType.Immediately, tc = stbase.futures.Constants.TimeConditionType.IOC
            )
        elif direction == stbase.Constants.Short:  # 卖开
            price = self.last_tick.price.last - 2
            # self.sell('rb2001', 0, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.LimitPrice,exchange_id='SHFE')
            self.sell(self.code, price, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.LimitPrice,
                      exchange_id=cs.exchange_id,
                        cc = stbase.futures.Constants.ContingentConditionType.Immediately,tc = stbase.futures.Constants.TimeConditionType.IOC
                      )
        else:
            print 'Error: Empty Operatoin "order_close()" '
            return

        data = OrderedDict(strategy_id=self.id, code=self.code, issue_time=datetime.datetime.now(),
                           oc=stbase.Constants.Close, direction=direction, vol=vol)
        record = model.TradeOrder()
        object_assign(record, data, True)
        record.save()
        cs.open_date = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)  # 记录开仓日期

        cs.save()

    def log_print(self,**kwargs):

        self.logger.debug(**kwargs)
        log = model.TradeMessageLog(**kwargs)
        log.strategy_id = self.id
        log.code = self.code
        log.save()

        # 推送到 redis broker
        log.issue_time = str(log.issue_time)
        self.pub_log_message.publish_or_produce(json.dumps(log.dict()))

    def order_open(self,price,direction,volume =1):
        """开仓
        n次超时限价委托保证所有量成交，否则下市价单,最终未成功报警处理，程序退出
        """
        self.siglog_print('order_open: ',price=price,direction=direction,volume = volume)
        self.siglog_print(**self.sig_params)

        if not self.order_enable :
            return

        cs = self.cs
        if not volume:
            volume = self.get_max_order_num(price) # 计算开仓数量

        # pos_water = self.get_position(direction)
        # pos_up = pos_water + volume
        times = 3
        time_wait = 10

        finished = False
        order_id = ''

        # vol = pos_up - pos_water
        vol = volume
        for _ in xrange(times):


            self.log_print(level=model.TradeMessageLog.INFO, title='order_open_limitprice',
                           message='price={} direction={} volume={}'.format(price, direction, vol))

            if direction == stbase.Constants.Long:  #  买开
                price = self.last_tick.price.BidPrice1
                # price = 4920
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.buy(self.code, price, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.LimitPrice,exchange_id=cs.exchange_id,
                        cc = stbase.futures.Constants.ContingentConditionType.Immediately, tc = tc
                )
            elif direction == stbase.Constants.Short:  # 卖开
                price = self.last_tick.price.AskPrice1
                # price = 4900
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.sell(self.code, price, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.LimitPrice,
                          exchange_id=cs.exchange_id,tc = tc
                          )

            self.log_print(level=model.TradeMessageLog.INFO, title='order_open_limitprice',
                           message='<< Return order_id={}'.format(order_id))

            num = self.product.trader.waitOrder(order_id,10)
            if num == vol:
                finished = True
                break
            # cancelOrder
            self.cancelOrder(order_id)

            #
            vol = volume - num
            if vol <= 0 :
                finished = True
                break



        if not finished:
            order_id = ''
            # if pos_water < pos_up:
            #     finished = False
            #     vol = pos_up - pos_water
            price = 0
            self.log_print(level=model.TradeMessageLog.INFO, title='order_open_anyprice',
                           message='price={} direction={} volume={}'.format(price, direction, vol))
            if direction == stbase.Constants.Long:  #  买开
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.buy(self.code, price, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.AnyPrice,exchange_id=cs.exchange_id,
                        tc = tc)
            elif direction == stbase.Constants.Short:  # 卖开
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.sell(self.code, price, vol, stbase.Constants.Open,stbase.futures.Constants.OrderPriceType.AnyPrice,
                          exchange_id=cs.exchange_id,tc = tc )

            self.log_print(level=model.TradeMessageLog.INFO, title='order_open_anyprice',
                           message='<< Return order_id={}'.format(order_id))
            num = self.product.trader.waitOrder(order_id,10)

            if num != vol:
                finished = False
                self.log_print(level=model.TradeMessageLog.ERROR, title='order_open_anyprice_error',
                               message='{} order volume:{} , traded num:{}'.format(order_id,vol,num ))
            else:
                finished = True

        #限价->市价 均委托不成功，则报警并退出
        if not finished:
            self.log_print(level=model.TradeMessageLog.INFO, title='order_open_error',message='委托失败, 关闭..')
            self.onTerminated()
            return


        #记录成交委托事件
        data = OrderedDict(strategy_id=self.id, code=self.code, issue_time=datetime.datetime.now(),
                           oc=stbase.Constants.Open, direction=direction, vol=volume)
        record = model.TradeOrder()
        object_assign(record, data, True)
        record.save()
        cs.open_date = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)  # 记录开仓日期
        cs.open_pos = volume    # 记录开仓数量
        cs.save()
        self.log_print(level=model.TradeMessageLog.INFO, title='order_open_okay', message='委托成功')

    def onTerminated(self):

        stbase.controller.stop()

    def _order_close(self,price , direction):
        """平仓 默认多头"""

        cs = self.cs

        vol = self.get_position(direction)
        if direction == stbase.Constants.Long: # 平多
            price = self.last_tick.price.last - 2
            self.sell(self.code,price,vol,stbase.Constants.Close,stbase.futures.Constants.OrderPriceType.LimitPrice,exchange_id=cs.exchange_id,cc = stbase.futures.Constants.ContingentConditionType.Immediately,tc = stbase.futures.Constants.TimeConditionType.IOC)
        elif direction == stbase.Constants.Short: # 平空
            price = self.last_tick.price.last + 2
            self.buy(self.code,price,vol,stbase.Constants.Close,stbase.futures.Constants.OrderPriceType.LimitPrice,exchange_id=cs.exchange_id,cc = stbase.futures.Constants.ContingentConditionType.Immediately,tc = stbase.futures.Constants.TimeConditionType.IOC)
        else:
            print 'Error: Empty Operatoin "order_close()" '
            return

        data = OrderedDict(strategy_id=self.id, code=self.code, issue_time=datetime.datetime.now(),
                           oc=stbase.Constants.Close, direction=direction, vol=vol)
        record = model.TradeRecord()
        object_assign(record, data, True)
        record.save()

    def test_shfe(self):
        self.code = 'rb2001'
        self.cs.exchange_id = 'SHFE'
        self.order_price_test = 3340


    def normalizeTimeContition(self,tc):
        if config.TRADE_API_CURRENT == config.TRADE_API_SIMNOW:
            return stbase.futures.Constants.TimeConditionType.IOC
        return tc

    def normalizeCloseTdFlag(self,exchange_id):
        if exchange_id == 'SHFE':
            return stbase.Constants.CloseToday
        return stbase.Constants.Close

    def normalizeCloseYdFlag(self,exchange_id):
        if exchange_id == 'SHFE':
            return stbase.Constants.CloseYesterday
        return stbase.Constants.Close


    def order_close(self,price , direction ,volume=1):
        """平仓 默认多头"""

        # self.test_shfe()

        self.siglog_print('order_close: ', price=price, direction=direction, volume=volume)
        self.siglog_print(**self.sig_params)

        if not self.order_enable:
            return

        cs = self.cs
        if not volume:
            volume = cs.open_pos

        times = 3
        time_wait = 10

        finished = False
        order_id = ''

        vol = volume

        for _ in xrange(times):

            if direction == stbase.Constants.Long:  # 买开
                price = self.last_tick.price.BidPrice1 # 买一价
                oc = self.normalizeCloseYdFlag(cs.exchange_id)
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.sell(self.code, price, vol, oc,
                                    stbase.futures.Constants.OrderPriceType.LimitPrice, exchange_id=cs.exchange_id,
                                    cc=stbase.futures.Constants.ContingentConditionType.Immediately,
                                    tc=tc
                                     )

            elif direction == stbase.Constants.Short:  # 卖开
                price = self.last_tick.price.AskPrice1
                oc = self.normalizeCloseYdFlag(cs.exchange_id)
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.buy(self.code, price, vol, oc,
                                     stbase.futures.Constants.OrderPriceType.LimitPrice,
                                     exchange_id=cs.exchange_id, tc=tc

                                     )

            self.log_print(level=model.TradeMessageLog.INFO, title='order_close_limitprice',
                           message='price={} direction={} volume={} order_id={}'.format(price, direction, vol,order_id))

            num = self.product.trader.waitOrder(order_id, 10)
            if num == vol:
                finished = True
                break
            # cancelOrder
            self.cancelOrder(order_id)

            vol = volume - num
            if vol <= 0:
                finished = True
                break

        # 执行市价单
        # pos = self.get_position(direction)
        # pos_water = pos
        if not finished:
            order_id = ''

            finished = False
            # vol =   pos_water - pos_down
            price = 0
            self.log_print(level=model.TradeMessageLog.INFO, title='order_close_anyprice',
                           message='price={} direction={} volume={}'.format(price, direction, vol))
            if direction == stbase.Constants.Long:  # 买开
                oc = self.normalizeCloseYdFlag(cs.exchange_id)
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.buy(self.code, price, vol, oc,
                                    stbase.futures.Constants.OrderPriceType.AnyPrice, exchange_id=cs.exchange_id,
                                    tc=tc)
            elif direction == stbase.Constants.Short:  # 卖开
                oc = self.normalizeCloseYdFlag(cs.exchange_id)
                tc = self.normalizeTimeContition(stbase.futures.Constants.TimeConditionType.GFD)
                order_id = self.sell(self.code, price, vol, oc,
                                     stbase.futures.Constants.OrderPriceType.AnyPrice,
                                     exchange_id=cs.exchange_id, tc=tc)

            self.log_print(level=model.TradeMessageLog.INFO, title='order_close_anyprice',
                           message='<< Return order_id={}'.format(order_id))

            num = self.product.trader.waitOrder(order_id, 10)

            if num != vol:
                finished = False
                self.log_print(level=model.TradeMessageLog.ERROR, title='order_close_anyprice_error',
                               message='{} order volume:{} , traded num:{}'.format(order_id, vol, num))
            else:
                finished = True


        # 限价->市价 均委托不成功，则报警并退出
        if not finished:
            self.log_print(level=model.TradeMessageLog.INFO, title='order_close_error', message='Order Failed , Terminating..')
            self.onTerminated()
            return

        # 记录成交委托事件
        data = OrderedDict(strategy_id=self.id, code=self.code, issue_time=datetime.datetime.now(),
                           oc=stbase.Constants.Close, direction=direction, vol=volume)
        record = model.TradeOrder()
        object_assign(record, data, True)
        record.save()
        cs.open_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # 记录开仓日期
        cs.save()
        self.log_print(level=model.TradeMessageLog.INFO, title='order_close_okay', message=' Order Success!')


    def siglog_print(self,*args,**kwargs):
        message =''
        for s in args:
            message += '{} '.format(s)
        if kwargs:
            message += ' '
        for k,v in kwargs.items():
            message+= "{}={} ,".format(k ,v)

        print message

        if not self.sig_log:
            curdate = current_date_string()
            name = os.path.join(PWD, 'sig-{}-{}.txt'.format(self.id, curdate))
            self.sig_log = open(name, 'w')

        self.sig_log.write(message)
        self.sig_log.write('\n')
        self.sig_log.flush()


        self.pub_log_trade.publish_or_produce(message)

        self.log_print(title='Signal',message = message)
        if not self.order_enable:
            return

        # model.TradeRecord Real Mode
        # tr  = model.TradeRecord()
        # tr.strategy_id = self.id
        # tr.code  = self.code
        # tr.issue_time = datetime.datetime.now()
        #
        # tr.save()


    def plot_view(self):
        """绘制运行状态数据"""
        fig, ax = plt.subplots(figsize=(24, 8))

        close = map(lambda _: _.close, self.plot_data.get('ks',[]))
        date = map(lambda _: _.datetime, self.plot_data.get('ks',[]))

        ax.plot(date, self.plot_data['up'], label='up')
        ax.plot(date, self.plot_data['down'], label='down')
        ax.plot(date, self.plot_data['mid'], label='mid')
        ax.plot(date, close, marker='.', label='close')
        # ax.scatter(range(num),close,marker='.',label='close')
        ax.legend()
        ax.grid(True)
        base64image = export_png_base64(fig)
        plt.cla()
        # ax.close()
        plt.close("all")
        view = model.StrategyRunningView()
        view.strategy_id = self.id
        view.code = self.code
        view.issue_time = datetime.datetime.now()
        view.data_base64 = base64image
        view.message = 'close:{} / mid:{} / up:{} / down:{} / open_days:{}  / v1:{} / v2:{}'.format(
                close[-1],self.plot_data['mid'][-1] , self.plot_data['up'][-1], self.plot_data['down'][-1],
                self.plot_data.get('open_days','' ), self.plot_data.get('v1'),self.plot_data.get('v2')
        )

        view.message += ' / R:{} / open_date: {}  / stopclose:{}'.\
            format( self.plot_data.get('R',''), str(self.plot_data.get('open_date','')) ,
                    self.plot_data.get('stopclose','')
                    )

        view.save()

    def exec_wr_atr(self):
        """策略
        前TIMEPERIOD时间缓冲周期内不参与计算
        """
        self.sig_params = OrderedDict()
        self.plot_data = OrderedDict()

        cs = self.get_code_params(self.code)
        self.cs = cs
        bars = self.market.getHistoryBars(self.code,'d',limit=500)
        ks = bars

        open_days = self.get_open_days(ks)



        a,b = ks[-2:]

        high = map(lambda _: _.high, ks)
        low = map(lambda _: _.low, ks)
        close = map(lambda _: _.close, ks)
        high = np.array(high, dtype=np.double)
        low = np.array(low, dtype=np.double)
        close = np.array(close, dtype=np.double)
        mid =(high + low + close ) /3.
        # print mid
        mid = ta.MA(mid, cs.TIMEPERIOD)
        # print mid
        atr = ta.ATR( high, low, close, cs.TIMEPERIOD)
        up = mid + atr * cs.N
        down = mid - atr * cs.N

        # td_open = self.last_tick.price.last # 最新成交价
        td_open = 0 # 对手价成交价

        v1  = (b.high + b.low + b.close ) / 3.
        v2  = (a.high + a.low + a.close ) / 3.
        close = b.close

        self.direction = cs.direction

        self.sig_params['mid'] = mid[-1]
        self.sig_params['up'] = up[-1]
        self.sig_params['down'] = down[-1]
        self.sig_params['v1'] = v1
        self.sig_params['v2'] = v2
        self.sig_params['close'] = close


        self.plot_data['mid'] = mid
        self.plot_data['up'] = up
        self.plot_data['down'] = down
        self.plot_data['ks'] = ks
        self.plot_data['open_days'] = open_days
        self.plot_data['v1'] = v1
        self.plot_data['v2'] = v2


        self.log_print(title='exec_wr_atr',message='direction:{} close:{} up:{} v1:{} v2:{}'.format(self.direction,close,up[-1],v1,v2))

        # LONG enter
        if self.direction in (stbase.Constants.Idle,stbase.Constants.Short) and close > up[-1] and v1 > v2:
            """
            1.空仓或空头
            2. close > up 
            3. td[ (high+low+close)/3] > yd [ (high+low+close)/3 ]
            """

            if self.direction == stbase.Constants.Short:
                self.order_close(td_open,direction=stbase.Constants.Short)  # 执行平仓操作

            cs.direction = stbase.Constants.Long
            self.order_open(td_open,direction=stbase.Constants.Long)

            if self.order_enable: # real 模式保存
                cs.save()
            return

        # SHORT enter
        if self.direction in  (stbase.Constants.Idle,stbase.Constants.Long) and close < down[-1] and v1 < v2:
            """
            1.空仓或多头（反手操作：先平再开) 
            2. close < down 
            3. td[ (high+low+close)/3] < yd [ (high+low+close)/3 ]
            """

            if self.direction == stbase.Constants.Long:
                self.order_close(td_open, stbase.Constants.Long)

            self.order_open(td_open,stbase.Constants.Short)
            cs.direction = stbase.Constants.Short

            if self.order_enable:  # real 模式保存
                cs.save()

            return

        # Leave 离场 zhi ying , zhi shun
        """止盈止损点触发离场
        计算：
        N = 100 日
        1. b日之前的R日的收盘均价 sma([b-n,b]/close) ， 与b日的收盘价比较
        2. 持仓的窗口参数 W ,  R = (N - W )  ( R >= 10 )  已开仓到b日的天数
              
        """

        if self.direction != stbase.Constants.Idle: # 非空仓
            R = cs.STOP_WIN - open_days
            if R < cs.STOP_WIN_MIN:
                R = cs.STOP_WIN_MIN

            stopclose = 0
            if self.direction in (stbase.Constants.Long,stbase.Constants.Short):
                # ks = self.product.market.getHistoryBars(bar.code, cycle='d', lasttime=b.time, limit=R*2)
                start = max( len(ks)-1 - R*2,0)

                # ks = self.bar_list[c.index - R*2 :c.index]
                ks = ks[ start:]

                stopclose = map(lambda _: _.close, ks)
                stopclose = np.array(stopclose, dtype=np.double)
                try:
                    stopclose = ta.MA(stopclose, R)
                except:
                    print 'error ..'

                stopclose = stopclose[-1]

            self.sig_params['R'] = R
            self.sig_params['open_days'] = open_days
            self.sig_params['open_date'] = str(self.cs.open_date)
            self.sig_params['stopclose'] = stopclose

            self.plot_data['R'] = R
            self.plot_data['open_days'] = open_days
            self.plot_data['open_date'] = str(self.cs.open_date)
            self.plot_data['stopclose'] = stopclose

            if self.direction == stbase.Constants.Long:
                if b.close < stopclose : # 昨日收盘价 < R 日收盘均价 ， 平多
                    self.order_close(td_open,stbase.Constants.Long)
                    cs.direction = stbase.Constants.Idle

                    if self.order_enable:  # real 模式保存
                        cs.save()

                else: # 未平仓处理 , 继续持仓中 , 今日收盘价 - 昨日收盘价
                    # bar.net = self.bar_list[bar.index-1].net + self.position * LOT_PER_UNIT * (td.close - b.close)
                    pass

            elif self.direction == stbase.Constants.Short: # 平空
                if b.close > stopclose:
                    # self.position -= 1  # 平空仓
                    # trade = OrderedDict(datetime=str(td.time), open=td.open, close=b.close, direction='short', oc='close',
                    #              price=td.open, num=1, stopclose = stopclose, open_days=self.open_days, r =R)

                    self.order_close(td_open,stbase.Constants.Short)

                    cs.direction = stbase.Constants.Idle

                    if self.order_enable:  # real 模式保存
                        cs.save()

                else:
                    # bar.net = self.bar_list[bar.index-1].net - self.position * LOT_PER_UNIT * (td.close - b.close)
                    pass



    def onTimer(self,timer):

        from mantis.sg.fisher.ctp import TickFix
        codes = self.get_codes()
        # obj = stbase.controller.futures.getTradeObject( codes[0].code )


        print self.get_amount()
        print self.get_position(stbase.Constants.Short)

        cs = self.get_code_params(self.code)
        self.cs = cs

        # cs = self.get_code_params(self.code)
        # self.cs = cs
        #
        if self.last_tick : # 必须获得行情tick
            # self.order_open(self.last_tick.price.last-2,stbase.Constants.Short)
            # stbase.controller.stop()
            # return

            # 检查商品的交易时间
            prd_name = TickFix.get_product_code(self.code).upper()
            p = TickFix.Products.get(prd_name)
            if p:
                if TickFix.is_in_trading_time(self.last_tick.price.time,p):  # and TickFix.is_in_trading_time( data['SaveTime'], p):
                    try:
                        # self.order_open(0, stbase.Constants.Long)
                        self.order_close(0, stbase.Constants.Long)
                        return
                        self.exec_wr_atr()
                    except:
                        traceback.print_exc()
                    self.plot_view()
                    stbase.println( 'Strategy Has Been Executed, Wait For Shutdown..' )
                    time.sleep(2)
                    stbase.controller.stop()
                else:
                    stbase.println( 'Not in Trading Time ,skipped..')
                    timer.start()
            else:
                stbase.println( 'System Config Error , code : {} Not In TickFix Table.'.format(self.code))
                stbase.controller.stop()
        else:
            timer.start()   # repeat
            print 'Market Is Closed.'


    def start(self):
        """不能在start 中调用 stbase.controller.stop()"""
        stbase.Strategy.start(self)
        stbase.println("Strategy : {} Started..".format(self.id))

        with open("{}.pid".format(self.id),'w') as f:
            f.write(str(os.getpid()))
            f.flush()
        self.set_params(pid = os.getpid())

        self.code = self.get_codes()[0].code

        self.log_print(message="Strategy Start..")


        if sys.argv[-1] == 'run': # 正式运行委托下单打开
            self.order_enable = True

        if self.order_enable:
            self.startTimer(timeout=2)   # 启动定时器，定时上报策略运行状态
        else:
            self.exec_wr_atr()  # 执行策略，仅仅输出信号文件
            self.plot_view()
            stbase.controller.stop()

def init_database(db_conn):
    from mantis.sg.fisher.model import model
    conn = db_conn
    db = conn[config.STRATEGY_DB_NAME]

    model.set_database(db)
    return db

def main():
    if len(sys.argv) <= 1:
        print 'Error: Need More Args!'
        return False

    strategy_id = sys.argv[1]

    # if not file_lock(os.path.join('/tmp',strategy_id)):
    #     print 'Error: Process Lock File Failed. Maybe Same Process Is Running. '
    #     return False

    # 初始化系统参数控制器
    paramctrl = stbase.MongoParamController()
    paramctrl.open(host= mongodb_host,port= mongodb_port,dbname= dbname)

    init_database(paramctrl.conn)   # 初始化数据库model
    # 策略控制器
    stbase.controller.init(data_path)
    # 添加运行日志处理
    stbase.controller.getLogger().addAppender(stbase.FileLogAppender('CTP'))
    stbase.controller.setParamController(paramctrl)

    param = paramctrl.get(strategy_id)  # 读取指定策略id的参数
    if not param:
        print 'Error: Strategy {} Not Found.'.format(strategy_id)
        return False

    if param.up_time:
        distance = datetime.datetime.now() - param.up_time
        if distance.seconds < 5:
            print 'Error: Same Strategy Is Running.. '
            return

    conn_url = paramctrl.get_conn_url(param.conn_url)  # 读取策略相关的交易账户信息
    conn_url.td_api_url = config.TRADE_API_URL
    conn_url.md_broker = config.MD_BROKER
    conn_url.pubsub_event_name = config.TRADE_PUBSUB_EVENT_NAME # 交易服务事件通知通道名称
    conn_url.save()
    # conn_url 存放交易和行情的所有运行配置信息
    # 初始化行情对象
    params = dict(db_conn=paramctrl.conn,md_broker=config.MD_BROKER)
    params.update(conn_url.dict())

    market = CtpMarket().init(**params)
    # 装备行情对象到股票产品
    stbase.controller.futures.setupMarket(market)
    # 初始化交易对象
    params = conn_url.dict()
    params['strategy_id'] = strategy_id
    trader = CtpTrader().init(**params)
    stbase.controller.futures.setupTrader(trader)

    # 初始化策略对象
    strategy = MyStrategy(strategy_id,stbase.controller.futures).init()

    #设置策略日志对象
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix= dbname,host=mongodb_host,port=mongodb_port))
    # 添加策略到 控制器
    stbase.controller.addStrategy(strategy)
    # 控制器运行
    # stbase.controller.run().waitForShutdown() # 开始运行 ，加载k线数据
    stbase.controller.run()
    # stbase.controller.stop()


if __name__ == '__main__':
    main()
