#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.amqp import AmqpManagerQPID


class QPIDServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'qpid')
        pass

    def init(self,cfgs):
        self._cfgs = cfgs
        AmqpManagerQPID.instance().init(cfgs)

    def open(self):
        AmqpManagerQPID.instance().open()

    def close(self):
        AmqpManagerQPID.instance().terminate()

    def getElement(self, name, category='queues'):
        return AmqpManagerQPID.instance().queues.get(name)


MainClass = QPIDServiceFacet

__all__ = (MainClass,)