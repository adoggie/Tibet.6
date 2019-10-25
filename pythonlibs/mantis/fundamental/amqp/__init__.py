#coding:utf-8

from mantis.fundamental.utils.useful import Singleton
from mantis.fundamental.amqp.base import MessageQueueType,AccessMode

from mantis.fundamental.amqp.conn_qpid import MQConnectionQpid


class AmqpManagerQPID(Singleton):
    def __init__(self):
        self.cfgs = None
        self.queues = {}

    def init(self,cfgs):
        if not cfgs:
            return
        self.cfgs = cfgs
        for cfg in self.cfgs.get('queues',[]):
            if cfg.get('enable',False) is False:
                continue
            mq = MQConnectionQpid(cfg)
            readwrite = 0
            if cfg.get('write',False):
                readwrite |= AccessMode.WRITE
            if cfg.get('read',False):
                readwrite |= AccessMode.READ

            self.queues[cfg.get('name')] = mq
            mq.rw = readwrite
        return self

    def getMessageQueue(self,name):
        return self.queues.get(name)

    def open(self):
        for q in self.queues.values():
            q.open(q.rw )

    def terminate(self):
        for mq in self.queues.values():
            mq.close()