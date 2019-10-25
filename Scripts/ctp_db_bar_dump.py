#coding:utf-8

"""
ctp_bar_dump.py
备份指定数据库

"""

import sys,time,os,datetime,traceback,os.path

dbs =['Ctp_Bar_1','Ctp_Bar_5','Ctp_Bar_15','Ctp_Bar_30','Ctp_Bar_60','Ctp_Bar_d']

host='127.0.0.1'
port=27017

data_dir='data'


for name in dbs:
    cmd = 'mongodump -h {} --port {} -d {} -o {}'.format(host,port,name,data_dir)
    print cmd
    os.system(cmd)

now = datetime.datetime.now()
timestr = 'ctp_db_bar-{}-{}-{}'.format(now.year,now.month,now.day)
cmd = 'tar cvzf {}.tar.gz {}'.format(timestr,data_dir)
print cmd
os.system(cmd)
print 'DB Dumping Work Finished!'
