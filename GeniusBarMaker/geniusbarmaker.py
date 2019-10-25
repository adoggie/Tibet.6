#coding:utf-8



import json
import copy
import json
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse
import requests


from mantis.sg.fisher.ctp import TickFix

from mantis.fundamental.redis.broker import MessageBroker
from mantis.fundamental.utils.useful import object_assign ,singleton
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
import config
from base import *
import worker

broker = MessageBroker()
bar_channel_pub = None

workerset_list = OrderedDict()

TickFix.ready()

def get_symbol_prefix(symbol):
    """合约类型 M,AU"""
    import re
    m = re.findall('^([A-Za-z]{1,3})\d{2,5}', symbol)
    if m:
        return m[0].upper()
    return ''

def quoteTickRecv( message, ctx):
    """Tick进入，推送到不同的k线周期处理对象"""
    # print '== current thread: ',threading.current_thread().ident

    data = message
    data = json.loads(data)

    # tick = TickData()
    # object_assign(tick, data, add_new=True)
    # 这个DateTime 是交易日YMD+ 当日HMS
    # 恶心的问题，在于非交易时间接收的tick的HMS居然也是错误的，shit，所以过滤是否有效tick要判断SaveTime字段了

    data['DateTime'] = datetime.datetime.strptime(data['DateTime'], '%Y%m%d %H:%M:%S.%f')
    # data['SaveTime'] = datetime.datetime.strptime(data['SaveTime'], '%Y%m%d %H:%M:%S.%f')
    data['SaveTime'] = datetime.datetime.now()

    # 剔除 savetime 与 datetime 相距1分钟的tick
    a = data['DateTime'].replace(2019,1,1)
    b = data['SaveTime'].replace(2019,1,1)
    if abs( datetime_to_timestamp(a) - datetime_to_timestamp(b) ) > 60:
        return


    a = data['DateTime']
    b = datetime.datetime.now()
    if a > b and (a - b).seconds > 120:
        # return
        pass

    symbol = data['InstrumentID']  # 合约名称
    prd_name = TickFix.get_product_code(symbol).upper()

    # where TradeData='2019-10-9'  order by SaveTime asc
    p = TickFix.Products.get(prd_name)
    if p:
        if TickFix.is_in_trading_time( data['DateTime'], p) : # and TickFix.is_in_trading_time( data['SaveTime'], p):
            rt = data['DateTime']
            # 夜盘时间
            if rt.time() >= datetime.time(hour=21) and rt.time() <= datetime.time(hour=23, minute=59, second=59,
                                                                                  microsecond=1000000 - 1):
                # 郑州以晚上21点开盘为交易日，其他交易所以隔日为交易日
                # 为保证夜盘时间在前，将非郑州的行情记录时间（21-00）算为交易日前一天晚间的记录,交易日跳跃多日的情况，夜间开盘日期会不准
                if p['exchange'] != 'ZCE':
                    rt = rt - datetime.timedelta(days=1)  # 夜盘期间的tick日期记录为交易日的前一天

            data['RealTime'] = rt
            day = data['TradingDay']  # 20190917
            trade_date = datetime.datetime.strptime(day, '%Y%m%d')
            data['TradeDate'] = trade_date

            time = '20001010 ' + data['UpdateTime'] + '.' + str(data['UpdateMillisec'])
            trade_time = datetime.datetime.strptime(time, '%Y%m%d %H:%M:%S.%f')
            data['TradeTime'] = trade_time
        else:
            return
    else:
        return


    tick = TickData()
    object_assign(tick,data,add_new=True)
    tick.datetime = data['RealTime']

    # print 'symbol:',tick.InstrumentID, ' datetime:',tick.DateTime

    symbol = tick.InstrumentID
    ws = workerset_list.get(symbol)
    if not ws:
        ws = worker.BarWorkerSet(symbol,onBar).init()
        workerset_list[symbol] = ws

    # if TickFilter().filter(tick):  # 是否有效时间段的tick
    ws.onTick(tick)

    # print 'quoteTickRecv End..'


def onBar(bar):
    """周期k线计算回调
       发送到redis通道，待CtpMarketDataRecorder 读取
    """
    if not bar:
        return
    # print bar
    # return

    # if not is_in_trading_time(bar.datetime):
    #     return

    scale = bar.cycle
    tablename = bar.symbol
    coll = config.db_conn['Ctp_Bar_{}'.format(scale)][tablename]
    coll.insert_one(bar.dict())
    print 'on bar () ', bar.symbol, bar.cycle, bar.datetime
    return

    data = bar.dict()

    data['datetime'] = data['datetime'].strftime('%Y%m%d %H:%M:%S.%f')
    data['trade_date'] = data['trade_date'].strftime('%Y%m%d %H:%M:%S.%f')
    # return
    message = json.dumps(data)
    bar_channel_pub.publish_or_produce( message )

    channelname = 'ctp.bar.pub_'+bar.symbol+'_'+str(bar.cycle)+'m'
    broker.conn.publish(channelname,message)

    print 'on bar () ',bar.symbol,bar.cycle,bar.datetime,'\n'



# @singleton
# class TickFilter(object):
#     """有效行情记录过滤器"""
#     def __init__(self):
#         pass
#
#     def filter(self,tick):
#         """判别tick是否有效 , 主要依据tick是否在交易时间段 (查表)
#         不同的商品各自的交易时间段均不同
#         """
#         dt = tick.DateTime
#         symbol = tick.InstrumentID
#         product = get_symbol_prefix(symbol)
#
#
#         return is_in_trading_time(tick.datetime)

# def is_in_trading_time(time):
#     time = time.time()
#     if time >= datetime.time(15, 30) and time < datetime.time(20, 55):
#         return False
#     if time >= datetime.time(10, 15) and time < datetime.time(10, 30):
#         return False
#     if time >= datetime.time(11, 30) and time < datetime.time(13, 0):
#         return False
#     if time >= datetime.time(2, 30) and time < datetime.time(8, 55):
#         return False
#     return True

@singleton
class TimedDriver(object):
    """时间驱动， 在分钟的第n秒触发 TickTimedBreak 信号"""
    def __init__(self):
        self.thread = threading.Thread(target=self.run)
        self.running = False
        self.last_time = None # datetime.datetime.time()

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.running = False

    def wait(self):
        time.sleep(1)
        self.thread.join()

    def run(self):
        self.running = True
        while self.running:
            if self.running == False:
                break
            time.sleep(1)

            if config.REAL: # 盘中运行时需打开 REAL ，将定时产生分钟break信号，触发前一个k线周期结束
                # pass
                self.time_drive()

    def time_drive(self):
        """每分钟的第秒触发一次 TickTimedBreak """
        N = 3
        now = datetime.datetime.now()
        if not self.last_time :
            if now.second > 3:
                for ws in workerset_list.values():
                    tick = TickTimedBreak()
                    ws.onTick( tick )
                self.last_time = now
        else:
            if self.last_time.minute != now.minute:
                """新的分钟切换"""
                self.last_time = None


def play_end():
    for ws in workerset_list.values():
        tick = TickTimedBreak()
        ws.onTick(tick)

def init_tick_subs():
    global bar_channel_pub

    channelname = 'ctp.tick.pub_*'
    # channelname = config.tick_sub + '*'
    channel = broker.createPubsubChannel(channelname, quoteTickRecv)
    channel.open()

    channelname = 'ctp.bar.pub'
    bar_channel_pub = broker.createChannel(channelname)
    bar_channel_pub.open()

def init_data():
    host, port, db, passwd = config.broker_url.split(':')
    broker.init(dict(host=host, port=port, db=db, password=passwd))
    broker.open()


def main():
    init_data()
    init_tick_subs()
    print 'Bar Maker Ready..'
    if config.REAL:
        TimedDriver().start().wait()


if __name__ == '__main__':
    config.REAL = True
    main()