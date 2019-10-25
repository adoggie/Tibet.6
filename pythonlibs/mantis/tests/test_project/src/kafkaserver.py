#coding:utf-8

import sys
import getopt

from camel.biz.application.corsrv import CoroutineApplication,setup,instance
from camel.fundamental.kafka import KafkaManager,READ,WRITE

class MyService(CoroutineApplication):
    def __init__(self):
        CoroutineApplication.__init__(self)

    def init(self):
        CoroutineApplication.init(self)
        KafkaManager.instance().init(self.getConfig().get('kafka_config'))


    def run(self):
        if sys.argv[-1] == 'client':
            KafkaManager.instance().getTopic('test').open(WRITE).produce('abc')
            print 'one message be sent out'
        else:
            KafkaManager.instance().getTopic('test').open(READ)
            CoroutineApplication.run(self)

    def _terminate(self):
        KafkaManager.instance().terminate()
        CoroutineApplication._terminate(self)

setup(MyService).run()


