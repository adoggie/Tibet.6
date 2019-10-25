#coding:utf-8

import os , os.path
from utils.timeutils import current_date_string
from stbase import MarketRecorder,TickData,BarData,StragetyLoggerAppender

from pymongo import MongoClient
from bson.objectid import ObjectId

class MarketMongoDBRecorder(MarketRecorder):
    """存储行情记录"""
    def __init__(self,db_prefix='',host='127.0.0.1',port= 27017, user='',password=''):
        MarketRecorder.__init__(self)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_prefix = db_prefix
        self.conn = MongoClient(host, port)

    def write(self, obj):
        dbname = ''
        collname = ''
        if isinstance(obj,TickData):
            dbname = 'Ticks'
            if self.db_prefix:
                dbname = self.db_prefix + '_' + dbname
                collname = obj.code

        if isinstance(obj,BarData):
            filename = '{}_{}_{}.bar'.format(obj.code,current_date_string(),obj.cycle)

            dbname = 'Bars'
            if self.db_prefix:
                dbname = self.db_prefix + '_' + dbname
                collname = obj.code + '_' + obj.cycle
        
        if not dbname:
            return
        
        data = obj.dict()
        db = self.conn[dbname]
        coll = db[collname]
        coll.insert_one(data)

    def open(self):
        pass

    def close(self):
        pass

#============================================================

class StragetyLoggerMongoDBAppender(StragetyLoggerAppender):
    """ 策略日志写入mongodb

        db: StrategyLogs_mystrategy
        每个策略一个db，策略启动生成一个新collection，
        命名: stname_ymdHMS
    """
    def __init__(self,db_prefix='StrategyLogs',host='127.0.0.1',port= 27017, user='',password=''):
        StragetyLoggerAppender.__init__(self)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_prefix = db_prefix
        self.cfgs ={}
        self.conn = MongoClient(host, port)

    def init(self,strategy,**kwargs):
        StragetyLoggerAppender.init(self,strategy)
        self.cfgs.update(kwargs)
        return self

    def output(self, data):
        """
        myst_20190201_100901
        :param data:
        :return:
        """
        # dbname = self.strategy.name
        # if self.db_prefix:
        #     dbname = self.db_prefix + '_' + dbname
        # db = self.conn[dbname]
        st = self.strategy.start_time
        # collname ='%s_%d%02d%02d_%0d%02d%02d'%(self.strategy.name,st.year,st.month,st.day,
        #                                        st.hour,st.minute,st.second)

        dbname = self.db_prefix
        db = self.conn[dbname]

        # collname = '%s_%d%02d%02d' % (self.strategy.name, st.year, st.month, st.day)
        collname = '%s' % (self.strategy.name,)

        coll = db[collname]
        del data['strategy']
        # print '='*20
        # print data

        coll.insert_one(data)

    def open(self):
        pass

    def close(self):
        self.conn.close()
        # print 'MongoConn Closed..'