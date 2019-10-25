#coding:utf-8


from collections import OrderedDict

from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.utils.importutils import import_class
from mantis.fundamental.application.app import instance

class ServiceBase(object):
    def __init__(self,name):
        self.name = name
        self.cfgs = {}

    def init(self, *args, **kwargs):
        raise NotImplementedError

    def start(self,*args,**kwargs):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def join(self):
        pass

    def getConfig(self):
        return self.cfgs


@singleton
class ServiceManager(object):
    def __init__(self):
        self.cfgs = {}
        self.services = OrderedDict()

    def init(self,cfgs):
        self.cfgs = cfgs
        for cfg in self.cfgs:
            if not cfg.get('enable',False):
                continue

            name = cfg.get('name')
            cls = import_class(cfg.get('class'))
            service = cls(name)
            # service.init(cfg,logger= instance.getLogger())
            service.init(cfg)
            self.services[name] = service
            print 'Initing Serivce: {} ..'.format(name)


    def start(self,block=False):
        for s in self.services.values():
            s.start(block)

    def stop(self):
        for s in self.services.values():
            s.stop()

        self.join()

    def join(self):
        for s in self.services.values():
            s.join()

    def get(self,name):
        return self.services.get(name)