#coding:utf-8

import os,os.path,traceback,time
import pymongo
import datetime
import config
import os

"""
扫描db中所有collection进行实践排序
"""
def make_bar(conn,collections=[] ):

    db = conn['Ctp_Tick']
    if not collections:
        collections = db.collection_names()

    log = open('make-log.txt','w')
    idx = 0
    for name in collections:
        if name == 'system.indexes':
            continue
        coll = db[name]
        print name,'indexing..'
        # print name
        os.system('python make-min-bar.py {}'.format(name))
        os.system('python make-day-bar.py {}'.format(name))
        # break
        idx+=1
        log.write('Working Process {}/{}'.format(idx,len(collections))-1)
        log.write('\n')
        log.flush()
    log.close()
conn = config.db_conn

make_bar(conn)
print 'Mark Bar Finished.'