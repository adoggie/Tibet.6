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

from base import *

class BarWorker(object):
    """k线周期工作者"""
    def __init__(self,manager,cycle):
        self.manager = manager
        self.cycle = cycle
        self.bar = None # BarData

    def onTick(self,tick):
        """到达的tick都是交易时间段的tick"""
        newbar = False
        switch = False

        while True:
            if not self.bar:
                if isinstance(tick,TickTimedBreak):
                    break
                newbar = True

                self.bar = BarData(self.cycle)
                self.bar.init(tick)  # 记住bar周期内出现的第一个tick时间

            # if self.cycle == BarCycle_60M:
            #     print '60'
            ret = self.bar.updateTick(tick)
            if ret == BarStatus_WaitMore:
                break

            if ret in (BarStatus_Closed,BarStatus_Broken):
                self.manager.onBarPop(self.bar)
                self.bar = None

            if ret == BarStatus_Broken:
                break

            if ret == BarStatus_Closed: # 带入下一个周期k线计算
                self.bar = BarData(self.cycle)
                self.bar.init(tick)


    def getBar(self):
        return self.bar

class BarWorkerSet(object):
    """多周期k线管理集合"""
    def __init__(self,symbol,onBar):
        self.symbol = symbol
        self.workers = []
        self.onBar_ = onBar

    def init(self, cycles = BarCycleList):
        for cycle in cycles:
            worker = BarWorker(self,cycle)
            self.addWorker( worker)
        return self

    def addWorker(self,worker):
        self.workers.append(worker)

    def onTick(self,tick):
        """将tick发送至多个周期的k线处理对象"""
        for worker in self.workers:
            worker.onTick(tick)

    def onBarPop(self,bar):
        """当周期计算完成时回调"""
        self.onBar_( bar )


