#coding:utf-8

import sys
import getopt

from camel.biz.application.celerysrv import CeleryApplication,setup,instance,celery

class MyService(CeleryApplication):
    def __init__(self):
        CeleryApplication.__init__(self)

setup(MyService).run()


