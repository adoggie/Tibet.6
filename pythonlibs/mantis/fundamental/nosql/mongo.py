# -*- coding: UTF-8 -*-

import smtplib,traceback,os,sys,time,os.path,base64


"""
http://api.mongodb.com/python/current/
https://api.mongodb.com/python/current/api/pymongo/collection.html

"""

from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs

class Connection:
    def __init__(self,dbname='test',host='localhost',port=27017,user='',password=''):
        self.addr = (host,port)
        self.dbname = dbname
        self.conn = MongoClient(host,port)
        self.db = self.conn[self.dbname]
        self.fs = None

    def getGridFs(self):
        if not self.fs:
            self.fs = gridfs.GridFS(self.db)
        return self.fs

    def new_file(self,filename):
        if not self.fs:
            self.fs = gridfs.GridFS(self.db)
        handle = None
        handle = self.fs.new_file(filename=filename)
        return handle # GridIn

    def put_file(self,content,filename=None):
        '''
            将content整个内容以文件方式存入，返回ObjectId()对象
        '''
        if not self.fs:
            self.fs = gridfs.GridFS(self.db)
        _id = self.put(content,filename = filename )
        return _id

    def remove_file(self,file_id):
        '''
            gridfs 中删除指定的文件存储
        '''
        if isinstance(file_id,str):
            file_id = ObjectId(file_id)
        self.fs.delete(file_id)


class Datasource(object):
    def __init__(self,cfgs):
        self.cfgs = cfgs
        self.conn = None
        self.dbname = None

    def open(self):
        db = self.cfgs.get('dbname')
        host = self.cfgs.get('host')
        port = self.cfgs.get('port')
        user = self.cfgs.get('user')
        passwd = self.cfgs.get('password')

        self.conn = MongoClient(host, port)

        return True

    def close(self):
        pass

    def write(self,collection,data,dbname='test'):
        db = self.conn[dbname]
        # db[collection].insert()