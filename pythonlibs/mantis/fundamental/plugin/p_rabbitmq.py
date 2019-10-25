#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.kafka import KafkaManager

class RabbitMQerviceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'rabbitmq')
        pass

    def init(self,cfgs):
        self._cfgs = cfgs


    def open(self):
        pass

    def close(self):
        pass


MainClass = RabbitMQerviceFacet
__all__ = (MainClass,)