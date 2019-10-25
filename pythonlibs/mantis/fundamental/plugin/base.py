#coding:utf-8

from mantis.fundamental.application import Application,instance

class BasePlugin(object):
    def __init__(self,id,type):
        self._id = id
        self._type = type
        self._cfgs = {}

    def init(self,cfgs):
        raise NotImplementedError

    def open(self):
        """operation can not be blocked"""
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def cfgs(self):
        return self._cfgs

    def getElement(self,name,category=None):
        return None

