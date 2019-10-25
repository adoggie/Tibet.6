#coding:utf-8

import pandas as pd
import numpy as np
from useful import hash_object
import os,os.path,traceback,time
import pymongo
import datetime

"""
扫描db中所有collection进行实践排序
"""
def init_db_index(conn,dbname,collections=[],index_name='datetime' , sort =pymongo.ASCENDING ):
    """
    初始化指定数据库数据集的索引
    :param dbname:  数据库名
    :param collections:集合名列表，空则扫描db下所有集合
    :param index_name:  索引名称
    :param sort:  排序类型，默认： 升序
    :return:
    """

    db = conn[dbname]
    if not collections:
        collections = db.collection_names()

    for name in collections:
        if name == 'system.indexes':
            continue
        coll = db[name]
        print name,'indexing..'
        coll.create_index([(index_name, sort,)])
        # print name

conn = pymongo.MongoClient('localhost',27018)
init_db_index(conn,'Ctp_Bar_d')
init_db_index(conn,'Ctp_Tick',index_name='DateTime_')
print 'Indexes Finished.'