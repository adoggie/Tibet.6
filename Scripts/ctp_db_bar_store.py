#coding:utf-8

"""
ctp_bar_restore.py
自动解压缩数据库dump包
删除当前重名的db
导入新的db脚本

"""

import sys,time,os,datetime,traceback,os.path
import pymongo

dbs =['Ctp_Bar_1','Ctp_Bar_5','Ctp_Bar_15','Ctp_Bar_30','Ctp_Bar_60','Ctp_Bar_d']

host='127.0.0.1'
port=27017

data_dir='data'

tarfile = sys.argv[1]

if not os.path.exists('data'):
    os.mkdir('data')

cmd = 'tar xvzf {} -C data'.format(tarfile)
print cmd
os.system(cmd)


conn = pymongo.MongoClient(host,port)


for name in dbs:
    print 'drop database {} ..'.format(name)
    conn.drop_database(name)
    if os.path.exists('data/{}'.format(dbs[0])):
        cmd = 'mongorestore -h {} --port {} -d {}  data/{}'.format(host,port,name,name)
    else:
        cmd = 'mongorestore -h {} --port {} -d {}  data/data/{}'.format(host,port,name,name)
    print cmd
    os.system(cmd)

print 'Work Finished!'
