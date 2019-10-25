#coding:utf-8

import time,datetime
import os,os.path
import json
import traceback
from threading import Thread,Condition
from Queue import Queue
from collections import OrderedDict

from mantis.fundamental.utils.timeutils import timestamp_current, timestamp_to_str,datetime_to_timestamp,\
    current_datetime_string,current_date_string,TimedTask
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.utils.useful import singleton

from base import *
import controller

class Market(object):
    """行情源 , 不同产品的接入行情方式不同，不同的券商接口"""

    Bars =['1m','5m','15m','30m','60m','d','w','m','q','y']

    def __init__(self,product):
        self.product = product
        self.generator = None
        self.recorder = None

        self.tick_handlers = OrderedDict()  # {code:[handler,],..}
        self.bar_handlers = OrderedDict()   # {code-bar:[handler,],...}  600232-1m:func,..
        self.thread = Thread(target=self.processThread)
        self.actived = False
        self.queue = Queue()

    def init(self,*args,**kwargs):
        self.setupGenerator(MarketGenerator())
        self.setupRecorder(MarketRecorder())
        return self

    def setupGenerator(self,generator):
        self.generator = generator
        self.generator.market = self
        return self

    def setupRecorder(self,recorder):
        self.recorder = recorder
        return self

    def open(self):
        # 开始行情接收
        if self.generator:
            # self.generator.open()
            pass
        if self.recorder:
            self.recorder.open()
        self.thread.start()
        return True

    def close(self):
        self.actived = False
        # self.thread.join()

    def initTradeObject(self,obj):
        return obj

    def subReset(self):
        """取消訂閱tick和bar"""
        self.tick_handlers = OrderedDict()
        self.bar_handlers = OrderedDict()
        return self

    def subTick(self,code,handler):
        """订阅行情周期"""
        obj =  self.product.getOrNewTradeObject(code)
        self.initTradeObject(obj)

        handlers = self.tick_handlers.get(code,[])
        if not handlers:
            self.tick_handlers[code] = [handler]
        else:
            handlers.append(handler)
        return obj

    def subBar(self,code,handler,cycle='1m'):
        """订阅k线数据"""
        key = '{}-{}'.format(code,cycle)

        obj = self.product.getOrNewTradeObject(code)
        self.initTradeObject(obj)

        handlers = self.bar_handlers.get(key, [])
        if not handlers:
            self.bar_handlers[key] = [handler,]
        else:
            handlers.append(handler)
        return obj

    def getHistoryBars(self,code,cycle,limit):
        """查询历史k线"""
        pass

    def onTick(self,tick):
        if not tick.trade_object:
            obj = self.product.getOrNewTradeObject(tick.code)
            tick.trade_object = self.product.market.initTradeObject(obj)

        self.tickInit(tick)

        handlers = self.tick_handlers.get(tick.code,[])
        for handler in handlers:
            handler(tick)
            if self.recorder:
                self.recorder.write(tick)
        tick.trade_object = None

    def tickInit(self,tick):
        tick.trade_object.setPrice(tick.price)

    def onBar(self,bar):
        if not bar.trade_object:
            obj = self.product.getOrNewTradeObject(bar.code)
            bar.trade_object = self.product.market.initTradeObject(obj)

        k = '{}-{}'.format(bar.code,bar.cycle)
        handlers = self.bar_handlers.get(k,[])
        for handler in handlers:
            handler(bar)
            if self.recorder:
                self.recorder.write(bar)

    def putData(self,data):
        """接收到的行情数据置入队列，等待被读取处理 """
        self.queue.put(data)

    def processThread(self):
        self.actived = True
        while self.actived:
            try:
                try:
                    data = self.queue.get(timeout=1)
                except:
                    continue

                if not data:
                    continue
                if isinstance(data,TickData):
                    self.onTick(data)
                if isinstance(data,BarData):
                    self.onBar(data)
            except:
                traceback.print_exc()
        # controller.getLogger().debug('Market Data Thread Exiting..')
        controller.TradeController().getLogger().debug( 'Market Data Thread Exiting..')
