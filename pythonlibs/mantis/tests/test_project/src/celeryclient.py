#coding:utf-8

import sys
import getopt

from camel.biz.application.celerysrv import CeleryApplicationClient,AsClient,setup,instance,celery

setup(CeleryApplicationClient)

instance.celeryManager.getService('test_server').send_task('access.celery.hello.hello',args=['sss',])



