#coding:utf-8

from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.nosql.mongo import MongoConnection


"""
mongodb 目前仅支持一个db源
"""
class MongoDBServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'mongodb')
        self.client = None

    def init(self,cfgs):
        self._cfgs = cfgs

    def open(self):
        dbname,host,port,user,passwd = self._cfgs.get('dbname','test'),\
            self._cfgs.get('host','localhost'), \
            self._cfgs.get('port','27017'), \
            self._cfgs.get('user',''), \
            self._cfgs.get('password','' )

        self.client = MongoConnection(dbname,host,port,user,passwd)


    def close(self):
        pass

    def select_db(self,name):
        return self.client.conn[name]

    def getElement(self, name='', category=''):
        return self.client


MainClass = MongoDBServiceFacet

__all__ = (MainClass,)