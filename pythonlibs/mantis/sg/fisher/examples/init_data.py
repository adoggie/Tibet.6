#coding:utf-8
"""
初始化策略运行控制参数
"""
from mantis.sg.fisher import model as model

strategies = [
    dict( strategy_id= 'TDX_Test1', conn_url='dongfang'),
    dict( strategy_id= 'AJ_Test1', conn_url='aijian'), # 爱建
]

connection_urls = [
    dict(id='dongfang',name=u'东方证券1',
         qsid=61,host="114.80.164.136",port=7708,
        version= "2.03",branch_id=1,account_type= 8 ,account_no ="06034051",
        trade_account_no = "06034051" , password = "060821",
        tx_password = "060821",
        client_account = "06034051",
        broker_account = "06034051",
        quote_host ="61.49.50.190",quote_port=7709,
         broker_name = "DONGFANG"
            ),
    dict(id='aijian',name=u'爱建证券1',
         qsid=35,host="139.224.94.170",port=7708,
        version= "6.57",branch_id=101,account_type= 9 ,account_no ="190120000330",
        trade_account_no = "190120000330" , password = "171025",
        tx_password = "171025",
        client_account = "190120000330",
        broker_account = "190120000330",
        quote_host ="61.49.50.190",quote_port=7709,
         broker_name = 'AIJIAN'
            ),

]

# CODES={
#     '002517': dict( name= u'愷英網絡' ,entity_id='SimpleMA',trigger='timer',timer_interval=2),
#     '600834': dict( name =u'申通地鐵' ,entity_id='SimpleMA',trigger='timer',timer_interval=2),
#     '600682': dict( name = u'南京新百' ,entity_id='ZFInDay',trigger='tick',timer_interval=0)
#        #  '600776':{ 'name': u'东方通信' },
#        # '601878': { 'name': u'浙商证券'},
#        # '600650': { 'name': u'锦江投资'},
#        # '300252': { 'name': u'金信诺' },
#        # '300310': { 'name': u'宜通世纪' },
#        # '600682': { 'name': u'南京新百'}
#        }


CODES={
    '002517':u'愷英網絡',
    '600834': u'申通地鐵' ,
        '600776': u'东方通信' ,
       '601878':  u'浙商证券',
       '600650':  u'锦江投资',
       '300252': u'金信诺' ,
       '300310': u'宜通世纪' ,
       '600682':  u'南京新百',
        '600460': u'士兰微',
        '600736': u'苏州高新',
        '600064': u'南京高科'
       }



code_settings = [
    dict(code= code,name= name,
         strategy_id = 'TDX_Test1',
         sub_tick = 1,
        sub_bar_1m = 1,
        sub_bar_5m = 1,
        sub_bar_15m = 1,
        sub_bar_30m = 1,
        sub_bar_60m = 1,
        enable = 1,
        max_qty = 100,
        algorithm = ''
    ) for code,name in CODES.items()
]

code_settings+=[
    dict(code= code,name= name,
         strategy_id = 'AJ_Test1',
         sub_tick = 1,
        sub_bar_1m = 1,
        sub_bar_5m = 1,
        sub_bar_15m = 1,
        sub_bar_30m = 1,
        sub_bar_60m = 1,
        enable = 1,
        max_qty = 100,
        algorithm = ''
    ) for code,name in CODES.items()
]

# entity_settings = [
#         dict(entity_id= 'SimpleMA',strategy_id='',code='',trigger='timer',timer_interval=2),
#         dict(entity_id= 'ZFInDay',strategy_id='',code='',trigger='tick',timer_interval=0),
# ]

def init_mongodb(dbname='TradeFisher',host='127.0.0.1',port=27017):
    from pymongo import MongoClient
    mg_conn = MongoClient(host, port)
    model.set_database(mg_conn[dbname])
    return mg_conn

def init_all(db):
    model.StrategyParam.collection().remove()
    for _ in strategies:
        sp = model.StrategyParam()
        sp.assign(_)
        sp.save()

    model.ConnectionUrl.collection().remove()
    for _ in connection_urls:
        url = model.ConnectionUrl()
        url.assign(_).save()

    model.CodeSettings.collection().remove()
    for _ in code_settings:
        cs = model.CodeSettings()
        cs.assign(_).save()

if __name__ == '__main__':
    db = init_mongodb(host='192.168.1.252')
    init_all(db)
    print model.ConnectionUrl.get()


