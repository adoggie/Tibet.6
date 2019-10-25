#coding:utf-8

# from flask.ext.redis import FlaskRedis
import redis
from mantis.fundamental.utils.useful import Singleton


"""
https://pypi.python.org/pypi/redis
https://redis.io/topics/quickstart

https://redislabs.com/lp/python-redis/

http://www.runoob.com/redis/redis-lists.html


"""



# class RedisCache:
#     def __init__(self,cfg):
#         self.type = cfg.get('type').lower()
#         self.name = cfg.get('name')
#         self.cfg = cfg
#         self.h = None
#
#     @property
#     def handle(self):
#         return self.h
#
#     def open(self):
#         host = self.cfg.get('host')
#         port = self.cfg.get('port')
#         passwd = self.cfg.get('password')
#         self.h = redis.StrictRedis(host, port,password=passwd)
#         return True
#
#     def get(self, key):
#         return self.h.get(key)
#
#     def set(self, key, value, expire=None):
#         self.h.set(key, value, expire)
#
#     def delete(self, key):
#         self.h.delete(key)
#
#     def close(self):
#         pass
#
#
#
#
#
#
#
#
# class CacheManagerRedis(Singleton):
#     def __init__(self):
#         self.cfgs = None
#         self.caches ={}
#
#     def get(self,name='default'):
#         return self.caches.get(name)
#
#     def init(self,cfgs):
#         """加载缓冲设备项目"""
#         if not cfgs:
#             return
#         self.cfgs = cfgs
#         for cfg in cfgs.get('backends',[]):
#             if cfg.get('enable') :
#                 redis = RedisCache(cfg)
#                 self.caches[cfg.get('name')] = redis
#
#         return self
#
#     def open(self):
#         for redis in self.caches.values():
#             redis.open()
#
#     def close(self):
#         for redis in self.caches.values():
#             redis.close()



class Datasource(object):
    def __init__(self, cfgs={}):
        self.cfgs = cfgs
        self.conn = None

    def open(self):
        host = self.cfgs.get('host','127.0.0.1')
        port = self.cfgs.get('port',6379)
        passwd = self.cfgs.get('password','')
        db = self.cfgs.get('db',0)
        self.conn = redis.StrictRedis(host, port, password=passwd, db=db)
        return True

    def close(self):
        pass

    

