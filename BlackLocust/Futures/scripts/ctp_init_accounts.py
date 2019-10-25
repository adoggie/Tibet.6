#coding:utf-8
"""
初始化ctp 交易账号
"""
import sys
from mantis.sg.fisher import model as model
import config

connection_urls = [
    dict(
        id = 'ctp-simnow',
        name = u'simnow',
        md_broker= config.MD_BROKER,
        td_api_url = config.TRADE_API_URL ,
        ),
    dict(
        id = 'zsqh-test',
        name = u'zsqh-test',
        md_broker= config.MD_BROKER,
        td_api_url = config.TRADE_INTERFACE_ZSQH_TEST ,
        ),

    dict(
        id = 'zsqh-prd',
        name = u'浙商期货实盘-prd',
        md_broker= config.MD_BROKER,
        td_api_url = config.TRADE_INTERFACE_ZSQH_PRD ,
        ),

]


def init_mongodb(host='127.0.0.1',port=27017,date = None):
    from pymongo import MongoClient
    dbname = config.STRATEGY_DB_NAME
    mg_conn = MongoClient(host, port)
    model.set_database(mg_conn[dbname])
    return mg_conn

def init_all(db):
    model.ConnectionUrl.collection().remove()
    for _ in connection_urls:
        url = model.ConnectionUrl()
        url.assign(_).save()

# 支持初始化指定的日期数据库
if __name__ == '__main__':
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[-1]
    db = init_mongodb(host= config.STRATEGY_SERVER[0] , port= config.STRATEGY_SERVER[1], date = date )
    init_all(db)
    print model.ConnectionUrl.get()


