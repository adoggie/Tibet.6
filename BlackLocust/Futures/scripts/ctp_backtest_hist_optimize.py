#coding:utf-8


"""
回测期货历史数据

在 ctp_backtest_hist.py 优化数据加载处理（一次记载所有历史记录集)

计算开始累计周期k线，在 period + 1 的 进行正式处理

1. 加入日净值序列计算

"""
import json
import numpy as np
import talib as ta
import pandas as pd
from dateutil.parser import parse

import os,os.path,sys
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
from mantis.sg.fisher import strecoder
from mantis.sg.fisher.stbase.base import BarDataEndFlag
from mantis.sg.fisher.ctp.backtest import CtpMarketBarBackTest

import config


strategy_id  ='EXPCTP_BACKTEST'
mongodb_host,mongodb_port = config.STRATEGY_SERVER

data_path = './ctp_zsqh-backtest'
dbname = config.STRATEGY_DB_NAME
quotas_db_conn = MongoClient(config.QUOTES_DB_SERVER[0],config.QUOTES_DB_SERVER[1]) # 历史k线数据库

"""================================="""

SYMBOL = u'CF'
DATASET = u'CF' #数据集
INDEX = ''

SAMPLE_DATE_RANGE =('2015-6-18 9:0' ,'2019-6-19 15:0')

STOP_WIN = 23  # 止盈止损 窗口日
STOP_WIN_MIN = 14
N = 1
TIMEPERIOD = 24

INIT_FUNDS = 1000 * 1000  # 100 w
LOT_PER_UNIT = 5 # 每手数, 最大乘数

FEE_HOP = 5  # 手续费每跳  手数 x 每手单位数量 x 每跳价格   5手 x 5吨 x5元 = 125
MARGIN_RATIO = 0.07 # 保证金率
MAX_MARGIN_AMOUNT = 0.2 # 保证金比例

class DAY_OC_FLAG(object):
    """
    当日开平仓标识
    """
    EMPTY =''
    OS ='os' # 开空仓
    OL ='ol' # 开多仓
    CS ='cs' # 平空
    CL ='cl' # 平多
    CSOL = 'csol' # 平空之后开多
    CLOS = 'clos' # 平多之后开空

class MyStrategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)
        self.bar_list = []  # 缓存所有进入的bar记录
        self.param_table ={}
        self.reset()

    def reset(self):
        self.product_close_array ={} # 收盘价array

        self.direction = 'idle' # [idle,long,short]

        self.order_bar = None # 委托下单 的k线
        self.open_days = 0 # 委托下单开始的交易日
        self.num = 1

        self.trade_table = [] # OrderedDict()
        self.last_bar = None

        self.open_times = 0  # 累计开仓次数
        self.close_times = 0  # 累计平仓次数

        self.amount_init = INIT_FUNDS # 初始资金
        self.amount = self.amount_init  # 100w
        self.margin_amount = 0 # 当前保证金数

        self.open_price = 0  # 开仓价格
        self.position = 0  # 持仓数量

        self.bar_count = 0
        
        self.fee_amount = 0 # 手续费总数

        self.output_file = None
        self.output_detail = './detail'
        if not os.path.exists(self.output_detail):
            os.mkdir(self.output_detail)

        self.fee = 0        # 当日交易手续费累计
        self.fee_in_day = 0 # 当日手续费
        self.net_list = [] # 净值序列 [k:v,..] , [{bar:net},...]

        self.day_oc = DAY_OC_FLAG.EMPTY

    def get_param(self,name,_defval):
        return self.param_table.get(name,_defval)

    def set_param(self,name,value):
        self.param_table[name] = value
        return self

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

    def bar_before(self,bar):
        self.fee = 0
        self.bar_count += 1
        self.last_bar = bar
        self.day_oc = DAY_OC_FLAG.EMPTY
        self.float_profit = 0
        self.fee_in_day = 0

        self.init_day_net(bar)

    def bar_after(self,bar):
        bar.position = self.position
        bar.direction = self.direction

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

        self.bar_before(bar)
        # print 'SYM：',bar.symbol, 'Time:',bar.time, 'High:',bar.high,'Low:',bar.low,'Open:',bar.open,'Close:',bar.close
        self.exec_wr_atr(bar)

        self.bar_after(bar)


    def onReachEnd(self):
        self.tradeFinished()
        print 'Reach End . Ready To Stop ..'

        self.reportView()

        # stbase.controller.stop()

    def tradeFinished(self):
        # 完成最后平仓
        if self.direction == 'idle':
            return
        self.position -=1

        # if self.direction ==  'long':

    def get_max_order_num(self,price):
        """计算可用下单委托数量"""
        usable = self.amount * MAX_MARGIN_AMOUNT
        fee = price * MARGIN_RATIO
        num = usable // fee // LOT_PER_UNIT
        return num

    def order_open(self,price):
        """开仓"""
        num = self.get_max_order_num(price)
        self.fee = num * LOT_PER_UNIT * FEE_HOP
        self.fee_amount += self.fee

        self.margin_amount = num * price * LOT_PER_UNIT *  MARGIN_RATIO
        self.amount -= self.margin_amount + self.fee
        self.open_price = price
        self.position = num #手数

        self.open_times +=1

        self.fee_in_day += self.fee

    def order_close(self,price , long_or_short='long'):
        """平仓 默认多头"""

        self.fee = self.position * LOT_PER_UNIT * FEE_HOP
        self.fee_amount += self.fee

        sum = (price - self.open_price) *  self.position * LOT_PER_UNIT
        if long_or_short == 'long':
            self.amount += sum
        else:
            self.amount -= sum

        self.amount += self.margin_amount - self.fee

        self.open_price = 0
        self.position = 0
        self.margin_amount = 0

        self.close_times +=1

        self.fee_in_day += self.fee

    def outline_print(self,kvs):
        info = OrderedDict(amount = self.amount, open_price = self.open_price , position = self.position , margin_amount = self.margin_amount)
        kvs.update(info)

    # def calc_net_profit(self,bar):

    def init_day_net(self,bar):
        """计算当日净值
        计算日净值
        空仓时当日净值就是昨日净值
        当日开仓，当日余额加保证金，加上收盘价格减去开仓乘以乘数
        当日平仓，就是当日余额加保证金
        持仓中，收盘价减去昨日收盘价

        """
        if bar.index == 0: # first line
            bar.net = self.amount + self.margin_amount
            return
        # 默认取前一天的净值
        if bar.time == parse('2015-08-07'):
            print 'stop'
        bar.net = self.bar_list[bar.index - 1].net




    def exec_wr_atr(self,bar):
        """策略
        前TIMEPERIOD时间缓冲周期内不参与计算
        """
        # ks = self.product.market.getHistoryBars(bar.code, cycle='d', lasttime=bar.time , limit=TIMEPERIOD*2)
        # start = max(bar.index+1 - TIMEPERIOD* 2,0)
        # start = max(bar.index - max(TIMEPERIOD*2,STOP_WIN),0)
        start = 0

        end =  bar.index+1
        ks = self.bar_list[ start :end ] # 包含本bar

        # period = max(TIMEPERIOD,STOP_WIN_MIN)
        period = TIMEPERIOD*2
        # if len(ks)< TIMEPERIOD +1 :
        if len(ks)< (period +1) :
            # print 'Stuff Me More Data..'
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

        num = self.get_max_order_num(td.open)

        # if bar.time ==parse('2016-07-28'):
        if bar.time ==parse('2015-08-14'):
            print 'stop'

        net = self.bar_list[bar.index - 1].net
        # LONG enter
        if self.direction in ('idle','short') and close > up[-1] and v1 > v2:
            """
            1.空仓或空头
            2. close > up 
            3. td[ (high+low+close)/3] > yd [ (high+low+close)/3 ]
            """

            if self.direction == 'short':
                # self.position -=1 # 平空仓
                trade = OrderedDict(datetime=str(td.time), open=td.open, close=td.close, direction='short', oc='close',
                             price=td.open, num=1)

                # net =  (td.open - b.close) * self.position * LOT_PER_UNIT
                # net *= -1
                net = net - (td.open - b.close) * self.position * LOT_PER_UNIT

                self.order_close(td.open,long_or_short='short')  # 执行平仓操作
                self.outline_print(trade)

                self.trade_table.append({'marks': '-- OC:close ,  From short To long --'})
                self.trade_table.append(trade)



            open = td.open # 开场价格开仓
            # self.position +=1 # 下一手
            self.direction = 'long'
            trade = OrderedDict(datetime= str(td.time), open=td.open, close = td.close, direction = 'long',oc='open',price = td.open, num = 1 )

            self.order_open(td.open)
            self.outline_print(trade)

            self.trade_table.append( trade )
            self.order_bar = bar

            self.open_days = 1

            # bar.net = self.amount  + self.margin_amount + net
            # bar.net += (收盘价 - 开仓价) * 持仓数 * 乘数
            # bar.net += (td.close - td.open) * self.position * LOT_PER_UNIT

            bar.net = net + (td.close - td.open) * self.position * LOT_PER_UNIT

            bar.net -= self.fee_in_day

            # bar.float_profit = bar.net - self.amount + self.margin_amount
            return

        net = self.bar_list[bar.index - 1].net

        # SHORT enter
        if self.direction in  ('idle','long') and close < down[-1] and v1 < v2:
            """
            1.空仓或多头（反手操作：先平再开) 
            2. close < down 
            3. td[ (high+low+close)/3] < yd [ (high+low+close)/3 ]
            """

            if self.direction == 'long':
                # do reverse 平仓再反向开仓
                # self.position -= 1  # 下一手
                self.trade_table.append({'marks': '-- OC:close ,  From long To short --'})
                trade = OrderedDict(datetime=str(td.time), open=td.open, close=td.close, direction='long', oc='close', price=td.open, num=1)

                net = net + (td.open - b.close) * self.position * LOT_PER_UNIT


                self.order_close(td.open,long_or_short='long')
                self.outline_print(trade)

                self.trade_table.append(trade)

                # self.amount += td.open - self.open_price

            if bar.time == parse('2015-08-6'):
                print 'stop'
            open = td.open # 开场价格开仓
            # self.position +=1 # 下一手
            self.direction = 'short'
            trade = OrderedDict(datetime= str(td.time), open=td.open, close = td.close, direction = 'short',oc='open',price = td.open, num = 1 )

            self.order_open(td.open)
            self.outline_print(trade)

            self.trade_table.append( trade )
            self.order_bar = bar
            self.open_days = 1

            # bar.net = self.amount  + self.margin_amount + net
            # bar.net -= (收盘价 - 开仓价) * 持仓数 * 乘数
            # bar.net -= (td.close - td.open) * self.position * LOT_PER_UNIT

            bar.net = net - (td.close - td.open) * self.position * LOT_PER_UNIT
            bar.net -= self.fee_in_day

            # bar.float_profit = bar.net - self.amount + self.margin_amount
            return

        # Leave 离场 zhi ying , zhi shun
        """止盈止损点触发离场
        计算：
        N = 100 日
        1. b日之前的R日的收盘均价 sma([b-n,b]/close) ， 与b日的收盘价比较
        2. 持仓的窗口参数 W ,  R = (N - W )  ( R >= 10 )  已开仓到b日的天数
              
        """
        if self.direction == 'idle': #空仓日净值等于前日净值
            bar.net =  self.bar_list[bar.index-1].net

        if self.direction != 'idle': # 非空仓
            R = STOP_WIN - self.open_days
            if R < STOP_WIN_MIN:
                R = STOP_WIN_MIN
            if self.direction in ('long','short'):
                # ks = self.product.market.getHistoryBars(bar.code, cycle='d', lasttime=b.time, limit=R*2)
                start = max(c.index - R*2,0)

                # ks = self.bar_list[c.index - R*2 :c.index]
                ks = self.bar_list[ start:c.index]

                stopclose = map(lambda _: _.close, ks)
                stopclose = np.array(stopclose, dtype=np.double)
                try:
                    stopclose = ta.MA(stopclose, R)
                except:
                    print 'error ..'

                stopclose = stopclose[-1]

            if self.direction == 'long':
                if b.close < stopclose : # 昨日收盘价 < R 日收盘均价 ， 平多
                    # self.position -= 1  # 下一手

                    trade = OrderedDict(datetime=str(td.time), open=td.open, close=b.close, direction='long', oc='close',
                                 price=td.open, num=1, stopclose=stopclose, open_days=self.open_days, r = R)

                    self.order_close(td.open,long_or_short='long')
                    self.outline_print(trade)

                    self.trade_table.append(trade)
                    self.open_days = 0
                    self.direction = 'idle'

                    # bar.net = self.amount + self.margin_amount

                    bar.net = net + (td.open - b.close) * self.position * LOT_PER_UNIT
                    bar.net -= self.fee_in_day

                else: # 未平仓处理 , 继续持仓中 , 今日收盘价 - 昨日收盘价
                    # bar.net = self.amount  + self.margin_amount
                    # bar.net += self.position * LOT_PER_UNIT *(td.close-b.close)
                    #
                    # bar.net += self.bar_list[bar.index-1].float_profit

                    bar.net = self.bar_list[bar.index-1].net + self.position * LOT_PER_UNIT * (td.close - b.close)

            elif self.direction == 'short': # 平空
                if b.close > stopclose:
                    # self.position -= 1  # 平空仓
                    trade = OrderedDict(datetime=str(td.time), open=td.open, close=b.close, direction='short', oc='close',
                                 price=td.open, num=1, stopclose = stopclose, open_days=self.open_days, r =R)

                    self.order_close(td.open,long_or_short='short')
                    self.outline_print(trade)

                    self.trade_table.append(trade)
                    self.open_days = 0
                    self.direction = 'idle'

                    # bar.net = self.amount + self.margin_amount

                    bar.net = net - (td.open - b.close) * self.position * LOT_PER_UNIT

                    bar.net -= self.fee_in_day
                else:
                    # bar.net = self.amount + self.margin_amount
                    # bar.net -= self.position * LOT_PER_UNIT * (td.close - b.close)
                    #
                    # bar.net += self.bar_list[bar.index - 1].float_profit
                    bar.net = self.bar_list[bar.index-1].net - self.position * LOT_PER_UNIT * (td.close - b.close)

    def reportView(self,fields):
        """输入运行报告"""
        idx = 1
        # fp = open('running_report_opt.txt','w')
        # fp = open(self.output_file,'w')
        fp = self.output_file
        name = "{}_{}-{}-{}-{}".format(SYMBOL,STOP_WIN,STOP_WIN_MIN,TIMEPERIOD,N)



        self.writeView('', fp)
        self.writeView(name+'.txt', fp)

        self.writeView(u'开仓次数:' + str(self.open_times), fp)
        self.writeView(u'平仓次数:' + str(self.close_times), fp)
        # fee = self.open_times *  OPENCLOSE_FEE
        fee = self.fee_amount

        self.writeView(u'手续费:' + str(fee), fp)
        # self.writeView(u'盈亏:' + str(self.amount - fee - self.amount_init), fp)
        self.writeView(u'盈亏:' + str(self.amount - self.amount_init), fp)
        self.writeView(u'样本周期:' + str(SAMPLE_DATE_RANGE), fp)
        self.writeView(u'样本数量:' + str(self.bar_count), fp)
        self.writeView(u'样本单位:' + str('D'), fp)
        self.writeView(u'初始资金:' + str(self.amount_init), fp)
        self.writeView(u'当前资金:' + str(self.amount), fp)
        self.writeView(u'当前保证金:' + str(self.margin_amount), fp)
        # self.writeView(u'最终权益:' + str(self.amount - fee - self.amount_init + self.margin_amount), fp)
        self.writeView(u'最终权益:' + str(self.amount  + self.margin_amount), fp)

        fields['params'].append(name)

        if not fields.has_key('stop_win'): fields['stop_win'] = []
        fields['stop_win'].append(STOP_WIN)

        if not fields.has_key('stop_win_min'): fields['stop_win_min'] = []
        fields['stop_win_min'].append(STOP_WIN_MIN)

        if not fields.has_key('time_period'): fields['time_period'] = []
        fields['time_period'].append(TIMEPERIOD)

        if not fields.has_key('n'): fields['n'] = []
        fields['n'].append(N)


        fields['open_times'].append(self.open_times)
        fields['close_times'].append(self.close_times)
        fields['fee'].append(fee)
        # fields['profit'].append(self.amount - fee - self.amount_init)
        fields['profit'].append(self.amount - self.amount_init)
        fields['date_range'].append(SAMPLE_DATE_RANGE)
        fields['sample_num'].append(self.bar_count)
        fields['sample_unit'].append('D')
        fields['init_funds'].append(self.amount_init)
        fields['curr_funds'].append(self.amount)
        fields['curr_margin'].append(self.margin_amount)

        if not fields.has_key('final_profit'): fields['final_profit'] = []
        # fields['close_profit'].append(self.amount - fee - self.amount_init + self.margin_amount)
        fields['final_profit'].append(self.amount  + self.margin_amount)

        # 准备写入交易细节
        filename = os.path.join(self.output_detail, name)
        fp_detail = open(filename,'w')
        fp = fp_detail

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

                text += " amount:{} position:{} margin_amount:{} open_price:{}".format(tr['amount'],
                                                                                       tr['position'],
                                                                                       tr['margin_amount'],
                                                                                       tr['open_price'])
                idx +=1

            self.writeView(text,fp)

        fp.close()

    def writeView(self,text,fp,newline=True ):
        text = text.encode('utf-8')
        fp.write(text)
        if newline:
            fp.write('\n')

    def onTimer(self,timer):
        print 'ontimer..'
        # timer.start()
        codes = self.get_codes()
        obj = stbase.controller.futures.getTradeObject( codes[0].code )


    def start(self):
        from table import make_table

        stbase.Strategy.start(self)
        stbase.println("Strategy : Sample Started..")

        cfgs = self.param_table
        params = cfgs.get("PARAMS")

        entries = []
        if not cfgs.get("TEST_ARRAY"):
            entries = make_table(params)
        else:
            entries = cfgs.get("TEST_ARRAY" )

        for idx, bar in enumerate(self.bar_list):
            bar.index = idx

        name_ov = 'runtest_overview_{}_{}.txt'.format(SYMBOL,INDEX)
        if os.path.exists(name_ov):
            os.remove(name_ov)

        # for pandas excel

        fields = OrderedDict(params=[],open_times=[], close_times=[],
                             fee=[],
                   profit=[],date_range=[],sample_num=[],
                   sample_unit=[],init_funds=[],curr_funds=[],curr_margin=[] )
        


        global STOP_WIN ,STOP_WIN_MIN ,N ,TIMEPERIOD,INIT_FUNDS ,LOT_PER_UNIT

        self.overview_report_ready()

        for p in entries:
            STOP_WIN = p['stop_win']
            STOP_WIN_MIN = p['stop_win_min']
            TIMEPERIOD = p['timeperiod']
            N = p['n']

            print '>>', STOP_WIN ,STOP_WIN_MIN ,N ,TIMEPERIOD
            # From Here
            self.reset()

            for bar in self.bar_list:
                self.onBar(bar)

            self.output_file = open(name_ov, 'a+')
            self.reportView(fields)

            # 净值处理
            self.data_net_report()

            self.overview_report_datarecord()


        self.overview_report_write()
        df = pd.DataFrame(fields)
        df.to_excel("runtest_overview_{}_{}.xlsx".format(SYMBOL,INDEX))


    def overview_report_ready(self):
        self.data_overview_dir = 'data-overview'
        if not os.path.exists(self.data_overview_dir):
            os.mkdir(self.data_overview_dir)

        self.overview_ds = OrderedDict()
        ds = self.overview_ds
        names = [u'名称',u'开仓次数',u'平仓次数',u'手续费',u'盈亏',u'样本周期',u'样本数量',u'样本单位']
        names += [u'初始资金',u'当前资金',u'当前保证金',u'最终权益',u'年化收益率',u'最大回撤',u'最长回撤时间']
        for _ in names:
            ds[_] = []

        self.overview_column_names = names

    def overview_report_write(self):
        name = "{}_{}-{}-{}-{}.xlsx".format(SYMBOL, STOP_WIN, STOP_WIN_MIN, TIMEPERIOD, N)
        # filename = os.path.join('running_overview_report', name)
        name = os.path.join(self.data_overview_dir,"running_overview_report_{}_{}.xlsx".format(SYMBOL,INDEX))
        filename = name

        df = pd.DataFrame(self.overview_ds, columns= self.overview_column_names)
        df.to_excel(filename)

    def data_net_report(self):
        """净值报告输出"""

        name = "{}_{}_{}-{}-{}-{}.xlsx".format(SYMBOL,INDEX, STOP_WIN, STOP_WIN_MIN, TIMEPERIOD, N)
        dirname = self.output_detail+'_NetProfit'
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        filename = os.path.join(dirname, name)


        net_list = map(lambda  _: (_.time,_.net,_.open,_.high,_.close,_.low,_.direction,_.position), self.bar_list)
        fields = OrderedDict(datetime = [], net = [] ,open=[],high=[],close=[],low=[] ,direction=[] ,position=[])
        for time,net,open,high,close,low,direction,position in net_list:
            fields['datetime'].append(time)
            fields['net'].append(net)
            fields['open'].append(open)
            fields['high'].append(high)
            fields['close'].append(close)
            fields['low'].append(low)
            fields['direction'].append(direction)
            fields['position'].append(position)

        df = pd.DataFrame(fields,columns=['datetime', 'net','open','high','close','low' ,'direction' ,'position'])
        df.to_excel( filename )

        # self.net_addition_report(net_list)

    def overview_report_datarecord(self):
        """从净值计算其他统计参数"""
        import base_function
        # df = pd.read_excel('detail_NetProfit/CF_X_22-20-10-1.xlsx')
        net = map(lambda _: _.net,self.bar_list)

        print base_function.linear(net)  # 线性回归计算年化收益率。输入为np.array输出为斜率（年化收益率）和截距
        print base_function.cal_maxdd(net)  # 返回最大回撤数据和开始结束的index
        print base_function.cal_maxdt(net)  # 最长回撤时间，返回周期数和开始结束index

        ds = self.overview_ds
        name = "{}_{}-{}-{}-{}".format(SYMBOL, STOP_WIN, STOP_WIN_MIN, TIMEPERIOD, N)

        ds[u'名称'].append(name)
        ds[u'开仓次数'].append(self.open_times)
        ds[u'平仓次数'].append(self.close_times)
        ds[u'手续费'].append(self.fee_amount)
        ds[u'盈亏'].append(self.amount - self.amount_init)
        ds[u'样本周期'].append(str(SAMPLE_DATE_RANGE))
        ds[u'样本数量'].append(len(self.bar_list))
        ds[u'样本单位'].append('D')
        ds[u'初始资金'].append(self.amount_init)
        ds[u'当前资金'].append(self.amount)
        ds[u'当前保证金'].append(self.margin_amount)
        ds[u'最终权益'].append(self.amount  + self.margin_amount)

        ds[u'年化收益率'].append( base_function.linear(net)[0] )
        ds[u'最大回撤'].append( base_function.cal_maxdd(net)[0] )
        ds[u'最长回撤时间'].append( base_function.cal_maxdt(net)[0] )


    # def net_addition_report(self,net_list):
    #     """从净值计算其他统计参数"""
    #     df = pd.read_excel('detail_NetProfit/CF_X_22-20-10-1.xlsx')
    #     # stdval = np.std(np.array(net_list['net']),ddof=1) # 非全体样本 偏差 n-1


def init_env(strategy):
    global SYMBOL,DATASET,SAMPLE_DATE_RANGE,INDEX
    global INIT_FUNDS,LOT_PER_UNIT,FEE_HOP,MARGIN_RATIO,MAX_MARGIN_AMOUNT

    cfgs = json.loads( open(sys.argv[1]).read())

    strategy.param_table.update(cfgs)

    SYMBOL = cfgs.get('SYMBOL',SYMBOL)
    DATASET = cfgs.get('DATASET',DATASET)
    SAMPLE_DATE_RANGE = cfgs.get('SAMPLE_DATE_RANGE',SAMPLE_DATE_RANGE)
    INIT_FUNDS = cfgs.get('INIT_FUNDS',INIT_FUNDS)
    LOT_PER_UNIT = cfgs.get('LOT_PER_UNIT',LOT_PER_UNIT)
    FEE_HOP = cfgs.get('FEE_HOP',FEE_HOP)
    INDEX = cfgs.get('INDEX', INDEX)
    MARGIN_RATIO = cfgs.get('MARGIN_RATIO',MARGIN_RATIO)
    MAX_MARGIN_AMOUNT = cfgs.get('MAX_MARGIN_AMOUNT',MAX_MARGIN_AMOUNT)

    return cfgs

        # return True

def main():
    if len(sys.argv) <= 1:
        print 'Error: Need More Args!'
        return False

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
        # params.update( conn_url.dict() )
    # market = CtpMarketBarBackTest().init(**params)      # 配置历史行情记录加载器
    market = CtpMarketBarBackTest().init()      # 配置历史行情记录加载器

    # 装备行情对象到股票产品
    # stbase.controller.futures.setupMarket(market)
    # 初始化交易对象
    # trader = CtpTrader().init(**conn_url.dict())
    # stbase.controller.futures.setupTrader(trader)

    # 初始化策略对象

    strategy = MyStrategy(strategy_id,stbase.controller.futures).init()
    cfgs = init_env(strategy)
    params = dict(db_conn=quotas_db_conn, cycle='d', symbol= cfgs['SYMBOL'], dataset= cfgs['DATASET'],
                  start=cfgs['SAMPLE_DATE_RANGE'][0], end=cfgs['SAMPLE_DATE_RANGE'][1], freq=0, wait=2)

    strategy.bar_list = market.loadHistBars(**params)

    #设置策略日志对象
    strategy.getLogger().addAppender(strecoder.StragetyLoggerMongoDBAppender(db_prefix= dbname,host=mongodb_host,port=mongodb_port))
    # 添加策略到 控制器
    stbase.controller.addStrategy(strategy)
    # 控制器运行
    # stbase.controller.run().waitForShutdown() # 开始运行 ，加载k线数据
    stbase.controller.run()





if __name__ == '__main__':
    main()
    # net_addition_report()
