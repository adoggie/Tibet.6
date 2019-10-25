# coding:utf-8

from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.basetype import ValueEntry

class ServiceType(object):
    UnDefined           = ValueEntry('undefined',u'未定义')
    GlobalDispatcher    = ValueEntry('dispatcher',u'调度服务器')
    MarketAdapter       = ValueEntry('market_adapter',u'行情适配器')
    TradeAdapter        = ValueEntry('trade_adapter',u'交易适配器')
    TradeServer         = ValueEntry('trade_server',u'交易服务器')
    DataResourceServer  = ValueEntry('data_res_server',u'数据资源服务器')
    DataPAServer        = ValueEntry('data_pa_server',u'数据处理和分析服务')
    StrategyRunner      = ValueEntry('strategy_runner',u'策略容器')
    StrategyDevRunner      = ValueEntry('strategy_dev_runner',u'策略容器')
    StrategyLauncher    = ValueEntry('strategy_launcher',u'策略加载器')
    FrontLauncher       = ValueEntry('front_launcher',u'前端服务加载器,负责交易/行情适配器的加载')
    XtpMonitor       = ValueEntry('xtp_monitor',u'')
    LatchetServer    = ValueEntry('latchet_server',u'消息转发到http-websocket')


class TimeDuration(object):
    SECOND     = 1
    MINUTE     = SECOND * 60
    HOUR       = MINUTE * 60
    MINUTE_1   = MINUTE
    MINUTE_2   = MINUTE * 2
    MINUTE_3   = MINUTE * 3
    MINUTE_5   = MINUTE * 5
    MINUTE_15  = MINUTE * 15
    MINUTE_30  = MINUTE * 30
    HOUR_1     = HOUR
    DAY        = HOUR * 24
    SCALES ={
        '1m':MINUTE_1,
        '2m':MINUTE_2,
        '3m':MINUTE_3,
        '5m':MINUTE_5,
        '15m':MINUTE_15,
        '30m':MINUTE_30,
        '60m':HOUR_1,
        '1h':HOUR_1,
        '1d':DAY
    }
TimeScale = TimeDuration

class ProductClass(object):
    # Undefined = ValueEntry('undefined',u'undefined')
    # Future  = ValueEntry('future',u'期货')
    # Stock   = ValueEntry('stock',u'股票')
    Undefined   = 'undefined'
    Future      = 'future'
    Stock       = 'stock'
    Coin        = 'coin'

class CryptoCoinType(object):
    Binance = 'binance'

class TradeAccount(object):
    """
    交易资金账户信息
    """
    NAME ='trade_account'
    def __init__(self):
        self.name = ''
        self.product = ''           # future , stock
        self.comment = ''
        self.connect = {}       # 连接配置信息，不同接入方式参数不同

    def loads(self,cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        return hash_object(self)

class TradeAccountQuota(object):
    """交易资金账户配额"""
    EMPTY_LIST = {}
    def __init__(self):
        self.name = ''
        self.account = ''       # 账户名称  TradeAccount.name
        self.limit = 10000
        self.product = ProductClass.Undefined
        self.props = {}
        self.channels = {}       # 交互通道
        self.trade_proxy = None # 交易代理对象
        self.order_ids = []

    def dumps(self):
        result = dict( name = self.name, account = self.account , limit = self.limit)

class TradeUserAccount(object):
    def __init__(self):
        self.user = ''
        self.quotas = TradeAccountQuota.EMPTY_LIST        # TradeAccountQuota

USER_NAME_UNDEFINED = ''

# class TradeSubAccountInfo(object):
#     """
#     交易开户资金子账户(系统内交易账户）
#     """
#     NAME = 'trade_sub_account'
#     def __init__(self):
#         self.account = ''
#         self.fund_limit = 0 # max fund quota for trade user
#
#     def loads(self, cfgs):
#         object_assign(self,cfgs)
#
#     def dumps(self):
#         result = hash_object(self)
#         return result


class TradeUserInfo(object):
    NAME = 'trade_user'
    def __init__(self):
        self.user = ''
        self.password = ''


    # def update(self,cfgs,prefix=''):
    #     if prefix :
    #         prefix+='.'
    #     prefix+=TradeUserInfo.NAME + '.'
    #     self.user  = cfgs.get(prefix+'user','')
    #     self.password  = cfgs.get(prefix+'password',0)
    #
    # def dict(self,prefix=''):
    #     if prefix:
    #         prefix+='.'
    #     prefix+=TradeUserInfo.NAME+'.'
    #     return hash_object(self,prefix,excludes=['NAME'])

    def loads(self, cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        result = hash_object(self)
        return result

# class DataBase(object):
#     def __init__(self):
#         self.gateway = ''
#         self.handler = None  # ProductHandler
#         self.product = ''
#
# class TickData(object):
#     def __init__(self):
#         self.symbol = ''
#         self.data = {}
#
#
# class BarData(object):
#     def __init__(self):
#         self.data = {}
#         self.symbol = ''
#         self.scale = '' # 1m,5m,..,1h,1d...
#         self.gateway =''
#         self.handler = None    # ProductHandler
#         self.product = ''



# class FutureTradeCommand(object):
#     ORDER_SELL = 'order_sell'
#     ORDER_SHORT = 'order_short'
#     ORDER_COVER = 'order_cover'
#



