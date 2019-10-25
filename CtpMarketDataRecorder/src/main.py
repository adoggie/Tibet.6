# coding:utf-8

from gevent.queue import Queue
# from threading import Thread
# from datetime import datetime, time

# from vnpy.event import EventEngine
# from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR,EVENT_TICK
# from vnpy.trader.vtEngine import MainEngine, LogEngine
# from vnpy.trader.gateway import ctpGateway
# from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData
from mantis.fundamental.application.app import instance

# from mantis.trade.service import TradeService,ServiceType,ServiceCommonProperty
from mantis.fundamental.application.service import BaseService

class DataResourceService(BaseService):
    def __init__(self,name):
        BaseService.__init__(self,name)
        self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        # self.thread = Thread(target=self.threadDataFanout)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()
        self.symbols = {} # 已经订阅的合约

    def init(self, cfgs,**kwargs):
        self.service_id = cfgs.get('id')
        # self.service_type = ServiceType.DataResourceServer
        super(DataResourceService,self).init(**cfgs)


    # def syncDownServiceConfig(self):
    #     TradeService.syncDownServiceConfig(self)

    def setupFanoutAndLogHandler(self):
        # from mantis.trade.log import TradeServiceLogHandler
        # self.initFanoutSwitchers(self.cfgs.get('fanout'))
        # handler = TradeServiceLogHandler(self)
        # self.logger.addHandler(handler)
        pass

    def start(self,block=True):
        # self.setupFanoutAndLogHandler()
        pass

        # 创建日志引擎
        super(DataResourceService,self).start()
        self.active = True
        # self.thread.start()


    def stop(self):
        super(DataResourceService,self).stop()
        if self.active:
            self.active = False
            # self.thread.join()

    def join(self):
        # self.thread.join()
        pass
