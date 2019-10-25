#coding:utf-8

"""
playTick.py
模拟测试Tick从mongodb读取 , 并发送到 redis队列 ，等待 GeniusBarMaker 读取并处理

"""


import json
import copy
import json
import sys
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse
import requests

from mantis.fundamental.redis.broker import MessageBroker
from mantis.fundamental.utils.useful import object_assign ,hash_object,singleton
import config
import geniusbarmaker as MakeBarMain

config.TEST = True
config.REAL = False

# symbol = 'm1909'
# symbol = 'AP910'
# symbol = 'i1909'
dbname = 'Ctp_Tick'


broker = MessageBroker()
bar_channel_pub = None

db = config.db_conn[dbname]
# coll = db[symbol]


def init_channel_pub(symbol):
    global bar_channel_pub

    host, port, db, passwd = config.broker_url.split(':')
    broker.init(dict(host=host, port=port, db=db, password=passwd))
    broker.open()

    channelname = config.tick_pub + symbol
    bar_channel_pub = broker.createPubsubChannel(channelname)
    bar_channel_pub.open()

def remove_collections(symbol):
    config.db_conn['Ctp_Bar_5'][symbol].remove()
    config.db_conn['Ctp_Bar_15'][symbol].remove()
    config.db_conn['Ctp_Bar_30'][symbol].remove()
    config.db_conn['Ctp_Bar_60'][symbol].remove()

def tick_local_store(symbol):
    db = config.db_conn[dbname]
    coll = db[symbol]

def dump_lock_ticks(symbol):
    """将db tick 记录下载到本地"""
    db = config.db_conn[dbname]
    coll = db[symbol]
    fp = open('{}.tick'.format(symbol),'w')
    coll.create_index([('SaveTime', 1)])
    rs = coll.find().sort('SaveTime', 1)
    index = 0
    for r in rs:
        r = dict(r)
        if r.has_key('DateTime_'):
            del r['DateTime_']
        del r['SaveTime']
        del r['_id']
        d = json.dumps(r)
        fp.write(d)
        fp.write('\n')
        index+=1
        if index %1000 == 0:
            print 'Record Index:',index

    fp.close()

def  play_local_ticks(symbol):
    fp = open('{}.tick'.format(symbol))
    while True:
        line = fp.readline()
        if not line : break
        line = line.strip()
        # message = json.loads(line)
        MakeBarMain.quoteTickRecv(line, None)

    print 'Play End.'



def remake_hist_bar(symbol):
    """指定生成历史k线 1 - 60 minutes"""
    remove_collections(symbol)
    init_channel_pub(symbol)

    coll = db[symbol]
    coll.create_index([('SaveTime', 1)])
    # rs = coll.find({'SaveTime':{'$gte':parse('2019-7-4 22:0:0'),'$lte':parse('2019-7-5 22:0:0')}}).sort('SaveTime',1)
    rs = coll.find().sort('SaveTime',1)
    # for r in list(rs): # 一次加载加速
    for r in rs:
        r = dict(r)
        if r.has_key('DateTime_'):
            del r['DateTime_']
        # del r['SaveTime']
        r['SaveTime'] = r['SaveTime'].strftime('%Y%m%d %H:%M:%S.%f')

        del r['_id']
        message = json.dumps(r)

        # bar_channel_pub.publish_or_produce(message)

        MakeBarMain.quoteTickRecv(message,None)
        # time.sleep(.001)
        # print 'pub tick..',symbol,r['DateTime']
    MakeBarMain.play_end()

    print 'play end..'

if __name__ == '__main__':
    # global symbol
    symbol = ''
    # if len(sys.argv) > 1:
    symbol = sys.argv[-1]

    # MakeBarMain.main()
    # time.sleep(2)
    remake_hist_bar(symbol)

    # dump_lock_ticks()
    # play_local_ticks()

    # time.sleep(1)

"""
db.getCollection('i1909').ensureIndex({'DateTime_':1})
"""