#coding:utf-8

import os
import psycogreen.gevent
psycogreen.gevent.patch_psycopg()
from gevent.pywsgi import WSGIServer
from gevent import spawn

import django
from django.core.handlers.wsgi import WSGIHandler
from mantis.fundamental.plugin.base import BasePlugin

class DjangoServiceFacet(BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'django')
        self.server = None


    def run(self):
        http = self._cfgs.get('http')
        host = http.get('host','127.0.0.1')
        port = http.get('port',5000)
        address = (host,port)
        self.server = WSGIServer(address, WSGIHandler())

        print 'Server: %s started, Listen on %s:%s ...'%(self.appId,host,port)
        self.server.start()
        self.server.serve_forever()


    def init(self,cfgs):
        self._cfgs = cfgs
        settings = cfgs.get('django_settings', 'django.settings')
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
        django.setup()

    def open(self,block=False):
        if block:
            self.run()
        else:
            spawn(self.run)


    def close(self):
        pass


MainClass = DjangoServiceFacet

__all__= (MainClass,)