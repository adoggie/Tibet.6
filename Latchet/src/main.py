# coding:utf-8

from mantis.fundamental.application.use_gevent import USE_GEVENT

if USE_GEVENT:
    from gevent.queue import Queue
else:
    from Queue import Queue

import json
import time
from threading import Thread
from collections import OrderedDict
import datetime

# from vnpy.trader.vtEvent import EVENT_LOG, EVENT_ERROR, EVENT_TICK, EVENT_CONTRACT
# from vnpy.trader.vtObject import VtSubscribeReq,VtTickData
from mantis.fundamental.application.app import instance
# from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.fundamental.application.service import BaseService
# from mantis.trade.constants import *

from mantis.sg.fisher.model import set_database


class MainService(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)

        # self.active = False  # 工作状态
        self.queue = Queue()  # 队列
        # self.thread = Thread(target=self.threadDataFanout)  # 线程
        self.ee = None
        self.mainEngine = None
        self.logger = instance.getLogger()
        self.symbols = {}  # 已经订阅的合约
        self.contracts = OrderedDict()
        self.ticks_counter = 0
        self.ticks_samples = []
        self.tick_filters = []
        self.contract_ticks = {}  # { symbol: tick }
        self.gatewayName = 'CTP'

    def init(self, cfgs, **kwargs):
        self.service_id = cfgs.get('id')
        # self.service_type = ServiceType.LatchetServer
        # super(MainService, self).init(cfgs)
        self.cfgs = cfgs
        BaseService.init(self, **kwargs)
        self.init_database()

    def init_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        db = conn['CTP_BlackLocust']
        set_database(db)
        return db

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self, block=True):
        import http.gateway   # 必须导入
        self.setupFanoutAndLogHandler()


        # 创建日志引擎
        super(MainService, self).start()
        self.active = True
        # self.thread.start()


    def stop(self):
        super(MainService, self).stop()
        self.mainEngine.exit()
        if self.active:
            self.active = False
            # self.thread.join()

    def join(self):
        # self.thread.join()
        pass

    def onTick(self,symbol, tickobj):
        pass

    # def threadDataFanout(self):
    #     """运行插入线程"""
    #     import traceback
    #     while self.active:
    #         try:
    #             # print 'current tick queue size:', self.queue.qsize()
    #             # dbName, collectionName, d = self.queue.get(block=True, timeout=1)
    #             tick = self.queue.get(block=True, timeout=1)
    #             symbol = tick.vtSymbol
    #
    #             #调试，仅允许调试合约发送
    #
    #             if self.cfgs.get('debug_symbols',[]):
    #                 if self.cfgs.get('debug_symbols').count(symbol) == 0:
    #                     continue
    #
    #             dt = datetime.datetime.strptime(' '.join([tick.date, tick.time]),'%Y%m%d %H:%M:%S.%f')
    #             tick.ts  = datetime_to_timestamp( dt )  # 合约生成时间
    #             tick.ts_host = int(time.time())         # 主机系统时间
    #             tick.mp = self.contracts.get(symbol).marketProduct # IF,AU,CU,..
    #
    #             # 传播到下级服务系统
    #             jsondata = json.dumps(tick.__dict__)
    #             self.dataFanout('switch0', jsondata, symbol=symbol)
    #
    #             # -- cache current tick into redis ---
    #             key_name = CtpMarketSymbolTickFormat.format(symbol = tick.vtSymbol)
    #             redis = instance.datasourceManager.get('redis').conn
    #             redis.hmset(key_name,tick.__dict__)
    #
    #             #-- cache for query --
    #             self.ticks_counter += 1
    #             if len(self.ticks_samples) > 2:
    #                 del self.ticks_samples[0]
    #             self.ticks_samples.append(tick.__dict__)
    #
    #         except Exception as e:
    #             # self.logger.error( str(e) )
    #             # traceback.print_exc()
    #             pass
    #
