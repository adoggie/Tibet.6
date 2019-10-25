#coding:utf-8

import sys
import getopt

from camel.biz.application.corsrv import CoroutineApplication,setup,instance
from camel.fundamental.amqp import AmqpManager,AccessMode

class MyService(CoroutineApplication):
    def __init__(self):
        CoroutineApplication.__init__(self)

    def init(self):
        CoroutineApplication.init(self)
        AmqpManager.instance().init(self.getConfig().get('amqp_config'))


    def run(self):
        if sys.argv[-1] == 'client':
            AmqpManager.instance().getMessageQueue('test').open(AccessMode.WRITE).produce('abc')
            print 'one message be sent out'
            CoroutineApplication.run(self)
        else:
            AmqpManager.instance().getMessageQueue('test').open(AccessMode.READ)
            CoroutineApplication.run(self)

    def _terminate(self):
        AmqpManager.instance().terminate()
        CoroutineApplication._terminate(self)

setup(MyService).run()


