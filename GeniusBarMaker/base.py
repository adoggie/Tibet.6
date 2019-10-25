#coding:utf-8

import datetime

from mantis.fundamental.utils.useful import hash_object
from mantis.fundamental.utils.timeutils import current_datetime_string

BarCycle_1M = 1
BarCycle_5M = 5
BarCycle_15M = 15
BarCycle_30M = 30
BarCycle_60M = 60
BarCycle_1D = 60*24

BarCycleList = (BarCycle_1M,BarCycle_5M,BarCycle_15M,BarCycle_30M,BarCycle_60M)
# BarCycleList = (BarCycle_1M,)
# BarCycleList = (BarCycle_60M,)
# BarCycleList = (BarCycle_15M,)


class TickData(object):
    def __init__(self):
        pass

class TickTimedBreak(object):
    """行情时钟分隔信号，在每分钟的第n秒触发产生"""
    def __init__(self):
        self.datetime = datetime.datetime.now() # 产生时间

BarStatus_WaitMore = 1  # 一个k线周期未完成
BarStatus_Closed = 2    # 一个k线周期结束，需要将带入的tick保持到下一个Bar周期
BarStatus_Broken = 3    # 一个k线周期结束 ,无需保持tick到下一个Bar周期


class BarData(object):
    def __init__(self , cycle):
        self.cycle = cycle

        self.datetime = None
        self.symbol = None
        self.exchange = None
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.openInterest = 0
        self.volume = 0

        self.last_volume = 0

        self.start = None   # 周期时间开始
        self.end = None     # 周期时间结束 ，但不包括 end

        self.trade_date = None # 交易日

    def dict(self):
        data =  hash_object(self,excludes=('last_volume','start','end'))
        return data


    def init(self,tick):
        # self.datetime = tick.DateTime
        self.datetime = tick.RealTime
        self.trade_date = tick.TradeDate

        self.symbol = tick.InstrumentID
        self.exchange = ''
        self.open = tick.LastPrice
        self.close = tick.LastPrice
        self.high = tick.LastPrice
        self.low = tick.LastPrice
        self.openInterest = tick.OpenInterest

        self.last_volume = tick.Volume

        # 计算周期
        N = self.datetime.minute / self.cycle
        min_start = N * self.cycle
        min_end = min_start + self.cycle

        self.start = self.datetime.replace(minute=min_start, second=0, microsecond=0)
        delta = datetime.timedelta(minutes= self.cycle)
        self.end = self.start + delta

        self.datetime = self.start
        # self.end = self.datetime.replace(minute=min_end, second=0, microsecond=0)
        print 'bar init: ',self.symbol , ' cycle:',self.cycle, 'From:',self.start , ' End:', self.end

    def updateTick(self,tick):
        """ """
        # if isinstance(tick, TickTimedBreak):
        #     return BarStatus_Broken

        if tick.datetime >= self.end or tick.datetime < self.start:
            if isinstance(tick,TickTimedBreak):
                return BarStatus_Broken
            else:
                return BarStatus_Closed

        if isinstance(tick,TickData):
            self.high = max(self.high,tick.LastPrice)
            self.low = min(self.low , tick.LastPrice)
            self.close = tick.LastPrice
            self.openInterest = tick.OpenInterest
            self.volume +=  tick.Volume - self.last_volume

        return BarStatus_WaitMore







