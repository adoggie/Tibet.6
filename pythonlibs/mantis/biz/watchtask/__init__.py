#coding:utf-8

import gevent
from camel.biz.application.camelsrv import CamelApplication,instance

def check_heartbeat(cfgs={}):
    repeat = True
    zk = instance.getZookeeper()
    if not zk:
        return False
    return repeat




