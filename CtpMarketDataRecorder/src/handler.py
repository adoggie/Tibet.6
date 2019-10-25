# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import datetime_to_timestamp
from mantis.fundamental.utils.useful import Sequence

CTP_TICK_DB_NAME ='Ctp_Tick'
CTP_BAR_DB_NAME = 'Ctp_Bar'

sequence = Sequence()

def get_message_on_ctp_ticks(message,ctx):
    data = message
    tick = json.loads(data)
    # dt = datetime.datetime.fromtimestamp(tick['Timestamp'])
    tick['DateTime_'] = datetime.datetime.strptime(tick['DateTime'], '%Y%m%d %H:%M:%S.%f')
    tick['SaveTime'] = datetime.datetime.now()

    a = tick['DateTime_']
    b = tick['SaveTime']
    if a > b and (a-b).seconds > 120:
        # return
        pass

    tablename = tick.get('InstrumentID')
    conn = instance.datasourceManager.get('mongodb').conn
    # 数据库名称可以配置在 settings.yaml 的 messagebroker 栏目 的channel.extra属性中
    dbname = ctx.get('channel').cfgs.get('extra',{}).get('db_name',CTP_TICK_DB_NAME)
    db = conn[dbname]
    table = db[tablename]
    table.insert_one(tick)

    print 'Tick Commited into DB.' , tick['InstrumentID'] , tick['DateTime']

def get_message_on_ctp_bars(message,ctx):
    # 写入计算完成的 k 线记录

    bar = json.loads(message)
    bar['datetime'] = datetime.datetime.strptime( bar['datetime'], '%Y%m%d %H:%M:%S.%f')

    tablename = bar.get('symbol')
    conn = instance.datasourceManager.get('mongodb').conn
    scale = str(bar.get('cycle',''))
    dbname = ctx.get('channel').cfgs.get('extra', {}).get('db_name', CTP_BAR_DB_NAME)
    dbname = dbname.format(scale=scale)
    db = conn[dbname]
    table = db[tablename]
    table.insert_one(bar)
    print 'Bar Commited into DB.', bar['symbol'], bar['cycle']