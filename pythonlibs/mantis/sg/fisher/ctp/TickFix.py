#coding:utf-8

"""
tickfix.py
修复不同交易所接收的tick时间
增加:
  RealTime  修正的行情时间，年月日为接收当日，时分秒为当日
 TradeDate  交易日 （日期型)

 郑州商品交易所  TradingDay 交易日 为夜盘开始的日期
 其他交易所 的交易日 为 日盘开始的日期

"""


import json
import copy
import json
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse
import requests

import pymongo


"""
ctp.sub_instruments = m2001,RM2001,y2001,c2001,AP2001,CF2001,a2001,hc2001,rb2001,ru2001,sc1911,jd2001,cu1911,TA2001,i2001,SF001,SM001,SR001,J2001,JM2001,AL2001,NI2001,PP2001


[(21,0,23,59),(0,0, 2,29),(9,0,10,14),(10,30,11,29),(13,30,14,59)],  1
[(21,0,22,59),(9,0,10,14),(10,30,11,29),(13,30,14,59)], 2 
[(21,0,23,29),(9,0,10,14),(10,30,11,29),(13,30,14,59)], 3
[(9,0,10,14),(10,30,11,29),(13,30,14,59)], 4
[(21,0,23,59),(0,0, 0,59),(9,0,10,14),(10,30,11,29),(13,30,14,59)],  5

M 2 DCE
RM 3 CZCE
Y 2 DCE
C 2 DCE
AP 4 CZCE
CF 3 CZCE
A 2 DCE
HC 2 SHFE
RB 2 SHFE
RU 2 SHFE
SC 1 SC
JD 4 CZCE
CU 5 SHFE
TA 3 CZCE
I 2 DCE
SF 4 CZCE
SM 4 CZCE
SR 3 CZCE
J 2 DCE
JM 2 DCE
AL 5 SHFE
NI 5 SHFE
PP 2 DCE
"""

TimeDefines ={
    # '1':[(21,0,23,59),(0,0, 2,29),(9,0,10,14),(10,30,11,29),(13,30,14,29)],
    1 : [(21,0,23,59),(0,0, 2,29),(9,0,10,14),(10,30,11,29),(13,30,14,59)],
    2 : [(21,0,22,59),(9,0,10,14),(10,30,11,29),(13,30,14,59)],
    3 : [(21,0,23,29),(9,0,10,14),(10,30,11,29),(13,30,14,59)],
    4 : [(9,0,10,14),(10,30,11,29),(13,30,14,59)],
    5 : [(21,0,23,59),(0,0, 0,59),(9,0,10,14),(10,30,11,29),(13,30,14,59)],
}

# 全部大写
ProductTimes = {
    'M': 2,
    'RM': 3,
    'Y': 2,
    'C': 2,
    'AP': 4,
    'CF': 3,
    'A': 2,
    'HC': 2,
    'RB': 2,
    'RU': 2,
    'SC': 1,
    'JD': 4,
    'CU': 5,
    'TA' :3,
    'I': 2,
    'SF': 4,
    'SM': 4,
    'SR': 3,
    'J': 2,
    'JM': 2,
    'AL': 5,
    'NI': 5,
    'PP': 2
}

SHE =dict( name='SHE',products=['HC','RB','RU','CU','AL','NI'] )
INE =dict( name='INE',products=['SC'] )
DCE =dict( name='DCE',products=['M','Y','C','A','I','J','JM','PP'] )
ZCE =dict( name='ZCE',products=['RM','AP','CF','JD','TA','SF','SM','SR'] )


ExchangeList = [SHE,DCE,ZCE,INE]


Products= {}

def ready():
    for ex in ExchangeList:
        for p in ex['products']:
            timedefs = TimeDefines[ProductTimes[p]]

            Products[p] = dict(exchange=ex['name'],time= timedefs)
    return Products

def get_product_code(symbol):
    """根据 合约代码名 得到 合约产品编码 ，例如: m1901 -> m """
    # digits = map(lambda _: chr(ord('0') + _), range(0, 10))
    import string
    code = symbol
    if symbol[-4] in string.digits:
        code = symbol[:-4]
    elif symbol[-3] in string.digits:
        code = symbol[:-3]
    return code

def is_in_trading_time(tick_time,prd_defs):
    """判别是否在交易时间段"""
    for seg in prd_defs['time']:
        start = datetime.time(hour=seg[0],minute=seg[1])
        end = datetime.time(hour=seg[2],minute=seg[3],second=59,microsecond=1000000-1)
        if tick_time.time() >= start and tick_time.time() <= end:
            return True

    return False

"""
db.getCollection('i2001').find({'SaveTime':{'$gte': ISODate('2019-09-03 0:0:55')}},{'DateTime_':1,'SaveTime':1,'OpenPrice':1,'TradingDay':1} ).sort({'SaveTime':1}).limit(100)

"""
def fix_ticks(conn,dbname,collections=[] ):
    db = conn[dbname]
    if not collections:
        collections = db.collection_names()


    for name in collections:
        if name == 'system.indexes':
            continue
        coll = db[name]

        for prdname,p  in Products.items():
            if not  name.startswith(prdname):
                continue
            print 'To be fixing..',name
            coll.create_index([('SaveTime', 1),('DateTime_',1),('TradingDay',1)])
            coll.update_many( {},{'$set': {'RealTime': None, 'TradeDate': None}}, upsert=True)

            rs = coll.find().sort('SaveTime',1)
            for r in rs:
                if not is_in_trading_time(r['DateTime_'],p):
                    continue
                rt = r['DateTime_']
                #夜盘时间
                if rt.time() >= datetime.time(hour=21) and rt.time() <= datetime.time(hour=23,minute=59,second=59):
                    if p['exchange'] != 'ZCE':
                        rt = rt - datetime.timedelta(days=1)

                day = r['TradingDay'] # 20190917
                trade_date = datetime.datetime.strptime(day, '%Y%m%d')
                coll.update_one({'_id':r['_id']},update={'$set':{'RealTime':rt,'TradeDate':trade_date}},upsert = True)

        # print name,'indexing..'

        # print name


def main():
    ready()
    conn = pymongo.MongoClient('localhost', 27018)
    fix_ticks(conn,'Ctp_Tick')


ready()

if __name__ == '__main__':
    # print get_product_code('sc2001')
    # print get_product_code('cu901')
    # print get_product_code('m1901')
    main()

"""
db.getCollection('i1909').ensureIndex({'DateTime_':1})
"""