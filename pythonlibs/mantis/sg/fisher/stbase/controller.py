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

from mantis.sg.fisher.stbase.base import *
from mantis.sg.fisher.stbase.product import *
from mantis.sg.fisher.stbase.logger import *

@singleton
class TradeController(object):
    """全局的交易控制器对象
    包含： 股票，期货等多个市场产品对象
    """
    def __init__(self):
        self.products= OrderedDict()
        self.data_path = ''
        self.strategies = OrderedDict()
        self.logger = Logger()
        self.condition = Condition()
        self.timed_task_list = []
        self.param_controller = ParamController()
        self.running = False

    def startTimer(self,back,user=None,timeout = 1):
        task = TimedTask(back,user,timeout)
        self.timed_task_list.append(task)
        task.start()

    def getDataPath(self):
        return self.data_path

    def removeTimer(self,task):
        task.stop()
        self.timed_task_list.remove(task)

    def registerProduct(self,product):
        self.products[product.name] = product

    def getProduct(self,name):
        return self.products.get(name)

    def init(self, data_path='./'):
        self.data_path = data_path
        # self.logger.addAppender(FileLogAppender())
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        self.param_controller = ParamController()
        return self

    def setLogger(self,logger):
        self.logger = logger

    def getLogger(self):
        return self.logger

    def setParamController(self,controller):
        self.param_controller = controller

    def getParamController(self):
        return self.param_controller

    @property
    def futures(self):
        """期货对象"""
        return self.products.get(Product.FUTURES)

    @property
    def stocks(self):
        """股票对象"""
        return self.products.get(Product.STOCKS)

    def run(self):
        self.running = True

        if self.stocks:
            self.stocks.open()
        if self.futures:
            self.futures.open()

        for name,st in self.strategies.items():
            # self.logger.info('strategy:{} start..'.format(name))
            st.start()

        self.waitForShutdown()

        for name,st in self.strategies.items():
            self.logger.info('strategy:{} end..')
            st.stop()

        if self.stocks:
            self.stocks.close()
        if self.futures:
            self.futures.close()

        self.param_controller.close()

        return self
        # self.waitForShutdown()

    def addStrategy(self,strategy):
        self.strategies[strategy.name] = strategy
        return self

    def stop(self):
        """策略控制器停止，回收所有分配的资源"""
        # self.condition.notify()

        # for name,st in self.strategies.items():
        #     self.logger.info('strategy:{} end..')
        #     st.stop()
        #
        # if self.stocks:
        #     self.stocks.close()
        # if self.futures:
        #     self.futures.close()
        #
        # self.param_controller.close()

        self.running = False
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()

    def waitForShutdown(self):
        # return
        self.logger.info('Waiting For Shutdown ..')
        if self.running:
            self.condition.acquire()
            self.condition.wait()
            self.condition.release()
        time.sleep(1)
        self.logger.info('Signaled. Cleaning Up..')