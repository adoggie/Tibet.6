#coding:utf-8

"""
make-day-bar.py
生成日线脚本

读取分钟k线，生成日线
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


symbol = 'm1909'
symbol = 'AP910'
symbol = 'i1909'

dbname = 'Ctp_Tick'



from base import BarData
def make_hist_day_bar(symbol,start,end='',dbname='Ctp_Bar_d'):
    """

    :param start: 2019-1-1
    :param end:  默认为至今
    :return:
    """
    coll = config.db_conn[dbname][symbol]
    start = parse(start)
    if not end:
        end =  datetime.datetime.now().date()
        end = datetime.datetime(year=end.year,month=end.month,day=end.day)

    coll.create_index([('datetime', 1)])
    coll.delete_many({'datetime':{'$gte':start,'$lte':end}})

    coll_m1 = config.db_conn['Ctp_Bar_1'][symbol]
    coll_m1.create_index([('datetime', 1)])

    seek_day = start
    # 依次迭代所有交易日
    while seek_day <= end:
        print 'Indexing ',seek_day
        rs = coll_m1.find({'trade_date':seek_day}).sort('datetime',1)
        bar = BarData('d')
        last_volume = 0
        count = 0
        for idx,r in enumerate(rs):
            count +=1
            bar.high = max(bar.high, r['high'])
            if idx ==0:
                bar.low = r['low']
            else:
                bar.low = min(bar.low, r['low'])

            bar.close = r['close']
            bar.openInterest = r['openInterest']
            last_volume = r['volume']
            if idx == 0:
                bar.open = r['open']
            else:
                bar.volume += r['volume'] - last_volume

        bar.datetime = seek_day

        if count:
            coll.insert_one( hash_object(bar) )

        seek_day += datetime.timedelta(days=1)

    print 'make day bar end..'

if __name__ == '__main__':
    # global symbol
    # if len(sys.argv) > 1:

    symbol = sys.argv[1]

    start = '2019-06-01'
    if len(sys.argv) >2 :
        start = sys.argv[2]

    make_hist_day_bar(symbol,start)

    # time.sleep(1)

"""
db.getCollection('i1909').ensureIndex({'DateTime_':1})
"""