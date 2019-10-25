#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.kafka import KafkaManager

class ZookeeperServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'zookeeper')
        pass

    def init(self,cfgs):
        self._cfgs = cfgs

    def open(self):
        pass

    def close(self):
        pass

MainClass = ZookeeperServiceFacet
__all__ = (MainClass,)