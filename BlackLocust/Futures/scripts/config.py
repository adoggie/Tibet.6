#coding:utf-8

MONGODB=('192.168.1.252',27017)
MONGODB=('127.0.0.1',27018)
# MONGODB=('192.168.1.252',27018)

STRATEGY_SERVER = MONGODB           # 策略运行记录数据库
STRATEGY_DB_NAME = 'CTP_BlackLocust'
QUOTES_DB_SERVER = MONGODB          # 行情历史k线数据库
TRADE_INTERFACE_SIMNOW = 'http://192.168.1.252:17001'

TRADE_INTERFACE_ZSQH_TEST = 'http://192.168.1.252:17001'
TRADE_INTERFACE_ZSQH_PRD = 'http://192.168.1.252:17001'     # 浙商期货
TRADE_INTERFACE_ZSQH_PRD = 'http://127.0.0.1:17001'     # 浙商期货

# TRADE_INTERFACE_SIMNOW = 'http://wallizard.com:17001'

TRADE_API_URL = TRADE_INTERFACE_ZSQH_PRD

# MD_BROKER='192.168.1.252:6379:0:'
MD_BROKER='127.0.0.1:6379:0:'
TRADE_PUBSUB_EVENT_NAME = 'zsqh-prd'


TRADE_API_SIMNOW = 1
TRADE_API_ZSQH = 2

TRADE_API_CURRENT = TRADE_API_SIMNOW

CRAWL_WORKTIME = (16,20)    # 每日 16 -20 之间


symbols ={
    'i2001':'tdx/I2001.txt',
    'ru2001':'tdx/RU2001.txt',
    'SR001': 'tdx/SR2001.txt',
    'jm2001': 'tdx/JM2001.txt',
    'TA001': 'tdx/TA2001.txt',
    'j2001': 'tdx/J2001.txt',
    'rb2001': 'tdx/RB2001.txt',
}

#爬取日k线数据
CRAWL_DAILY_SYMBOLS= {
    'i2001':'I2001',
    'ru2001':'RU2001',
    'SR001':'SR2001',
    'jm2001':'JM2001',
    'TA001':'TA2001',
    'j2001':'J2001',
    'rb2001':'RB2001',

}
