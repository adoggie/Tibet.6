# coding:utf-8

__doc__ = u'celery 功能管理类'


from celery import Celery
from camel.fundamental.utils.useful import Singleton
from service import CeleryService


class CeleryManager(Singleton):
    def __init__(self):
        self.conf = {}

        self.available_svcs = {}
        self.current = None


    def init(self,cfgs):
        if not cfgs: return self

        self.conf = cfgs
        # self._initChannels()
        self._initServices()
        name = self.conf.get('current',[])

        svc = self.available_svcs.get(name)
        if svc:
            self.current = svc
        return self

    def getService(self,name=''):
        svc = self.available_svcs.get(name)
        return svc

    @property
    def app(self):
        return self.current.app

    def _initServices(self):
        cfg_svcs = self.conf.get('services',[])

        for cfg in cfg_svcs:
            svc = CeleryService(cfg)
            self.available_svcs[svc.name] = svc





