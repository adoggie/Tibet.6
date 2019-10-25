#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from camel.fundamental.celery.manager import CeleryManager

class CeleryServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'kafka')
        pass

    def init(self,cfgs):
        self._cfgs = cfgs
        CeleryManager.instance().init(cfgs)

    def open(self):
        if CeleryManager.instance().current:
            CeleryManager.instance().current.open()

    def close(self):
        pass


MainClass  = CeleryServiceFacet

__all__ = (MainClass,)