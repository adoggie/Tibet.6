# coding:utf-8


from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.utils.importutils import import_class

@singleton
class DatasourceManager(object):

    def __init__(self):
        self.cfgs = {}
        self.datasources = {}

    def init(self,cfgs):
        self.cfgs = cfgs
        for c in self.cfgs:
            if not c.get('enable',False):
                continue
            cls = import_class(c.get('class'))
            ds = cls(c)
            ds.open()
            self.datasources[ c.get('name')] = ds

    def open(self):
        for _,ds in self.datasources.items():
            ds.open()

    def close(self):
        for ds in self.datasources.values():
            ds.close()

    def get(self,name):
        return self.datasources.get(name)




