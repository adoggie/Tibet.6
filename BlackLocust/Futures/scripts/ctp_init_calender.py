#coding:utf-8
"""
初始化ctp 交易日历
"""
import sys
from mantis.sg.fisher import model as model
import config

all_days =[
    # ( today , prev_day )  prev_day 为空默认给前一日
    ('2019-9-23','2019-9-20'),
    ('2019-9-24',None), # 默认前一日，
    ('2019-9-25',None),
    ('2019-9-26',None),
    ('2019-9-27',None),
    ('2019-10-8',None),
]

def init_days(conn):
    db = conn[config.STRATEGY_DB_NAME]
    db['Calender'].remove()

    for _ in all_days:
        url = model.ConnectionUrl()
        url.assign(_).save()


def init_mongodb(host='127.0.0.1',port=27017,date = None):
    from pymongo import MongoClient
    dbname = config.STRATEGY_DB_NAME
    mg_conn = MongoClient(host, port)
    model.set_database(mg_conn[dbname])
    return mg_conn

# 支持初始化指定的日期数据库
if __name__ == '__main__':
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[-1]
    db = init_mongodb(host= config.STRATEGY_SERVER[0] , port= config.STRATEGY_SERVER[1], date = date )
    init_days(db)


