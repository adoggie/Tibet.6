#coding:utf-8

import datetime

from mantis.fundamental.nosql import model as model_
from mantis.fundamental.nosql.model import Model
from mantis.fundamental.utils.useful import object_assign

class StrategyParam(Model):
    """策略运行参数"""
    def __init__(self):
        Model.__init__(self)
        self.strategy_id = ''          # 策略名称
        self.start = 0          # 启动时间
        self.conn_url = ''      # 连接信息标识
        self.status = ''        #  running, paused,stopped
        self.run = 0            # 0 停止， 1 允许运行
        self.enable = 0         # 0 不启用 ,1 启用
        self.start_time = None  #
        self.up_time = None     # 最近活跃时间
        self.run_test_params = ''
        self.run_real_params = 'run' # 运行参数

class ConnectionUrl(Model):
    """交易通道相关的账户和服务器连接信息"""
    def __init__(self):
        Model.__init__(self)
        self.id = ''            # 标识
        self.name = ''
        # self.type  = '1'        # 账户类型
        # self.qsid = 0
        # self.host = "" # 交易服务器
        # self.port = 0            # 交易服务器
        # self.version = ""
        # self.branch_id = 0
        # self.account_type = 0,
        # self.account_no = ""
        # self.trade_account_no = ""
        # self.password = ""
        # self.tx_password = ""
        # self.client_account = ""
        # self.broker_account = ""
        # self.quote_host = ''             # 行情服务器
        # self.quote_port = 0           # 行情服务器
        # self.broker_name = ''

class CodeSettings(Model):
    """交易产品控制"""
    def __init__(self):
        Model.__init__(self)
        self.code = ''          #  证券代码
        self.name = ''          # 证券名称
        self.strategy_id = ''   # 策略标识
        self.sub_tick = 1       # 是否订阅
        self.sub_bar_1m = 1
        self.sub_bar_5m = 1
        self.sub_bar_15m = 1
        self.sub_bar_30m = 1
        self.sub_bar_60m = 1
        self.enable = 1          #是否可用
        # self.max_qty = 0        # 最大持仓数量
        # self.algorithm = ''     # 对应的算法
        self.entity_id = ''     # 证券代码同时只能绑定一个策略实体对象
        self.limit_buy_qty = 0  # 今日最大买入数量
        self.limit_sell_qty = 0  # 今日最大卖出数量
        self.open_allow =True   # 开仓允许
        self.cover_allow = True #平仓允许
        self.oc_last = ''     # 前一次开仓还是平仓状态

class CodeSettingsParamType(Model):
    """parameter type defines"""

    def __init__(self):
        Model.__init__(self)
        self.code = ''  # 证券代码
        self.strategy_id = ''  # 策略标识
        self.name = ''  # Parameter Name
        self.type = '' # int,float,str,bool,datetime


class CodeSettingsInited(Model):
    """合约初始化参数值，仅作为还原使用"""
    def __init__(self):
        Model.__init__(self)
        self.code = ''          #  证券代码
        self.name = ''          # 证券名称
        self.strategy_id = ''   # 策略标识
        self.sub_tick = 1       # 是否订阅
        self.sub_bar_1m = 1
        self.sub_bar_5m = 1
        self.sub_bar_15m = 1
        self.sub_bar_30m = 1
        self.sub_bar_60m = 1
        self.enable = 1          #是否可用
        # self.max_qty = 0        # 最大持仓数量
        # self.algorithm = ''     # 对应的算法
        self.entity_id = ''     # 证券代码同时只能绑定一个策略实体对象
        self.limit_buy_qty = 0  # 今日最大买入数量
        self.limit_sell_qty = 0  # 今日最大卖出数量
        self.open_allow =True   # 开仓允许
        self.cover_allow = True #平仓允许
        self.oc_last = ''     # 前一次开仓还是平仓状态


class CodePrice(Model):
    """ 记录股票当前价格
        fields : stbase.Price
    """
    def __init__(self):
        Model.__init__(self)
        self.code = None
        self.name = None


class CodePosition(Model):
    """当前股票的持仓记录
        fields ： stbase.Position
    """
    def __init__(self):
        Model.__init__(self)
        self.code = None
        self.name = None
        self.strategy_id = None

class CodeBasicInfo(Model):
    """证券交易产品的基础信息"""
    def __init__(self):
        Model.__init__(self)
        self.code = None
        self.name = ''

class CodeCommissionRate(Model):
    """手续费"""
    def __init__(self):
        Model.__init__(self)
        self.code = None
        self.name = ''

class CodeMarginRate(Model):
    """保证金"""
    def __init__(self):
        Model.__init__(self)
        self.code = None
        self.name = ''

class EntitySettings(Model):
    """交易运算实体对象配置参数"""
    def __init__(self):
        Model.__init__(self)
        self.entity_id = ''     # 自身标识
        self.strategy_id = ''   # 策略标识 (冗余)
        self.code = ''          # 证券代码 (冗余)
        self.max_pos_qty = 0    # 最大持仓数量
        self.trigger = 'tick'   # 触发类型 tick,bar,timer
        self.timer_interval = 0 # 如果是定时器触发，则指定定时器间隔



class ServerAddress(Model):
    """TDX的服务器"""
    def __init__(self):
        Model.__init__(self)
        self.type = "1"
        self.ip = ''
        self.port = 0


class TradeOrder(Model):
    """交易委托记录"""
    def __init__(self):
        Model.__init__(self)
        self.strategy_id = ''
        self.code = ''
        self.issue_time = None
        self.oc = ''    #Open,Close
        self.direction = '' #Long,Short
        self.price = 0
        self.vol = 0        # 量
        self.lot = 0        #
        
        self.commit_time = None

        self.trans_id = ''  # 交易编号
        self.status = ''    # 交易完成状态, 未成，部分成，全成
        self.commit_vol = 0 # 实际成交数量
        self.commission = 0 # 手续费


class TradeMessageLog(Model):
    """交易日zi"""
    DEBUG ='debug'
    WARN ='warn'
    INFO = 'info'
    ERROR = 'error'
    FATAL = 'fatal'

    def __init__(self,level= DEBUG,**kwargs):
        Model.__init__(self)
        self.strategy_id = ''
        self.code = ''
        self.issue_time = datetime.datetime.now()
        self.level = level
        self.title = ''
        self.message = ''
        object_assign(self,kwargs,True)


class StrategyRunningView(Model):
    def __init__(self):
        Model.__init__(self)
        self.strategy_id = ''
        self.code = ''
        self.issue_time = datetime.datetime.now()
        self.data_base64 = '' # 历史运行绘制的行情图
        self.message = ''

class StrategyOrderLog(Model):
    """交易委托历史"""
    def __init__(self):
        Model.__init__(self)
        self.strategy_id = ''
        self.issue_time = datetime.datetime.now()

class StrategyTradeLog(Model):
    """交易成交历史"""
    def __init__(self):
        Model.__init__(self)
        self.strategy_id = ''
        self.issue_time = datetime.datetime.now()


class StrategyErrorLog(Model):
    def __init__(self):
        Model.__init__(self)
        self.strategy_id = ''
        self.issue_time = datetime.datetime.now()
        self.conn_url = ''

# 以下代碼必須保持，在每一個模塊的model中必須複製,以便於支持 Model在不同的數據庫中
var_locals = locals()

def set_database(database):
    model_.set_database(var_locals,database)

