#coding:utf-8

"""
导入指定的历史期货日线数据
"""
import pandas as pd
import numpy as np
from useful import hash_object
import os,os.path,traceback,time
import pymongo
import datetime

#ctp期货文件目录
orign_data_path = '/home/samba/data/20190910-futrues-data/Data'


class BarData(object):
    def __init__(self , cycle='D'):
        self.cycle = cycle

        self.datetime = None
        self.symbol = None
        self.exchange = None
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.openInterest = 0
        self.volume = 0

        self.last_volume = 0

        self.start = None   # 周期时间开始
        self.end = None     # 周期时间结束 ，但不包括 end

    def dict(self):
        data =  hash_object(self,excludes=('last_volume','start','end'))
        return data


conn = pymongo.MongoClient('localhost',27017)
db = conn['Ctp_Bar_d']

for filename in os.listdir(orign_data_path):

    filename = filename.decode('utf-8')
    if filename.find('~lock')!=-1 or filename.find('~$')!=-1:
        continue

    index = filename.find(u'指数')
    if index == -1:
        print 'skipped file..',filename
        continue

    print filename

    prd_name = filename[:index] # 期货产品名
    data = pd.read_excel( os.path.join(orign_data_path,filename) )
    # print data
    # print data.head(2)
    # print data.loc[2]
    colnames =  data.columns[1:7]
    rows =  data[ colnames].values
    # rows = rows[pd.notnull(rows['日期'])]
    rows = filter(lambda r: not isinstance(r[0],type(np.NAN)),rows)
    # print rows
    # last = rows[-1]
    # print isinstance(last[1] , type( pd.NaT ))
    # print isinstance(last[0], type(np.NAN))
    # # print last[1],type(last[1])
    db[prd_name].remove()
    coll = db[prd_name]

    """名称         日期   开盘价(元)   最高价(元)   最低价(元)   收盘价(元)"""
    for r in rows:
        bar =BarData()
        bar.cycle = 'D'
        # print r
        # print str(r[1])
        bar.datetime = datetime.datetime.strptime( str(r[1]),'%Y-%m-%d %H:%M:%S')
        bar.symbol = prd_name
        bar.open = float(r[2])
        bar.high = float(r[3])
        bar.low = float(r[4])
        bar.close = float(r[5])
        d = bar.dict()
        coll.insert_one(d)

    # print data.iloc[1:3][:2]
    # print data[ [u'名称',u'日期',u'开盘价(元)'] ][:2]
    # break
