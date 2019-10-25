#coding:utf-8

"""
通达信行情 日线数据每日导入

"""
import os,os.path
from dateutil.parser import parse
from mantis.sg.fisher import stbase
import pymongo
from dateutil.parser import parse
import config

def loadQuoteBars(quote_file,code,ktype='d'):
    bars = []
    lines = open(quote_file).readlines()
    lines = map(str.strip, lines)
    # if not code:
    #     code = lines[0].split(' ')[0]
    lines = lines[2:-1]
    for line in lines:
        fs = line.split()
        # ymd, hm, open_, high, low, close, vol, amount = fs[:8]
        # dt = ymd + ' ' + hm[:2] + ':' + hm[2:] + ':00'

        ymd, open_, high, low, close, vol = fs[:6]
        dt = parse(ymd)

        bar = stbase.BarData()
        bar.code = code
        bar.cycle = ktype
        bar.open = float(open_)
        bar.high = float(high)
        bar.low = float(low)
        bar.close = float(close)
        bar.vol = float(vol)
        bar.amount = float(0)
        bar.time = dt
        bar.datetime = bar.time
        bars.append(bar)
    return bars



def importQuoteBarsIntoMongoDB(conn,code,quote_file,ktype='d'):
    print 'importing ',code,' ...'
    bars = loadQuoteBars(quote_file,code,ktype)
    db = conn['Ctp_Bar_{}'.format(ktype)]
    coll = db[code]
    coll.remove()
    for bar in bars:
        r = coll.find_one({'datetime': bar.time})
        if r:
            continue
        coll.insert(bar.dict())

    coll.create_index([('datetime', 1,),('time', 1,)])
    print '\tbars:',len(bars)



def init_mongodb(host='127.0.0.1',port=27017,date = None):
    from pymongo import MongoClient
    dbname = 'Ctp_Bar_d'
    mg_conn = MongoClient(host, port)
    # model.set_database(mg_conn[dbname])
    return mg_conn

conn = init_mongodb(config.MONGODB[0],config.MONGODB[1])

for symbol,filename in config.symbols.items():
    basedir = '../../Data'
    filename = os.path.join(basedir,filename)
    importQuoteBarsIntoMongoDB(conn,symbol,filename)