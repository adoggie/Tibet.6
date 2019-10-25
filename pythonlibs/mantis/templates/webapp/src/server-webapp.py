#coding:utf-8


from mantis.fundamental.application.use_gevent import use_gevent
use_gevent()

from mantis.fundamental.application.app import Application,instance,setup

setup(Application).init().run()



