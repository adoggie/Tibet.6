#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.kafka import KafkaManager

class KafkaServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'kafka')
        pass

    def init(self,cfgs):
        self._cfgs = cfgs
        KafkaManager.instance().init(cfgs)

    def open(self):
        KafkaManager.instance().open()

    def close(self):
        KafkaManager.instance().terminate()

    def getElement(self, name, category='topic'):
        return KafkaManager.instance().topics.get(name)



MainClass  = KafkaServiceFacet

__all__ = (MainClass,)