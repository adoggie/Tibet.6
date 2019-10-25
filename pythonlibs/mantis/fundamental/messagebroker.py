# coding: utf-8

from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.utils.importutils import import_class


@singleton
class MessageBrokerManager(object):

    def __init__(self):
        self.cfgs = {}
        self.brokers = {}

    def init(self,cfgs):
        self.cfgs = cfgs
        for cfg in self.cfgs:
            if not cfg.get('enable',False):
                continue
            cls = import_class(cfg.get('class'))
            broker = cls()
            broker.init(cfg)
            broker.open()
            self.brokers[ cfg.get('name')] = broker

    def get(self,name):
        return self.brokers.get(name)


    def start(self):
        for b in self.brokers.values():
            b.open()

    def stop(self):
        for b in self.brokers.values():
            b.close()
