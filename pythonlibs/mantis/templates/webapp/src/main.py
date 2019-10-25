# coding:utf-8


import os,sys
from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.fundamental.application.service import BaseService
from optparse import OptionParser

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


    def get_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        return conn['smartvision']

    def getDbModel(self):
        from mantis.fanbei.smartvision import model
        return model