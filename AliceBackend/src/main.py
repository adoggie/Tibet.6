# coding:utf-8


import os,sys
from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.fundamental.application.service import BaseService
from optparse import OptionParser
from mantis.sg.fisher.model import set_database

class MainService(BaseService):
    def __init__(self,name):
        BaseService.__init__(self,name)
        self.logger = instance.getLogger()
        self.servers = {}
        self.command_controllers ={}

    def init(self, cfgs,**kwargs):
        # self.parseOptions()
        self.cfgs = cfgs
        BaseService.init(self,**kwargs)
        self.init_database()


    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self,block=True):
        BaseService.start(self)
        # CheckProcessController().init().start()

    def stop(self):
        BaseService.stop(self)

    def initCommandChannels(self):
        pass
        # TradeService.initCommandChannels(self)
        # channel = self.createServiceCommandChannel(CommandChannelTradeAdapterLauncherSub,open=True)
        # self.registerCommandChannel('trade_adapter_launcher',channel)


    def init_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        db = conn['CTP_BlackLocust']
        set_database(db)
        return db

    def getDbModel(self):
        from mantis.fanbei.smartvision import model
        return model