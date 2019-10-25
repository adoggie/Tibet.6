#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.redis.datasource import CacheManagerRedis

class RedisServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'redis')
        pass

    def init(self,cfgs):
        self._cfgs = cfgs
        CacheManagerRedis.instance().init(cfgs)

    def open(self):
        CacheManagerRedis.instance().open()

    def close(self):
        CacheManagerRedis.instance().close()

    def getElement(self, name='default', category='backend'):
        return CacheManagerRedis.instance().caches.get(name)


MainClass = RedisServiceFacet

__all__ = (MainClass,)