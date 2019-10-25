#coding:utf-8
import time,datetime
import os,os.path
import json
import traceback
from threading import Thread,Condition
from Queue import Queue
from collections import OrderedDict

from mantis.fundamental.utils.timeutils import timestamp_current, timestamp_to_str,datetime_to_timestamp,\
    current_datetime_string,current_date_string,TimedTask
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.utils.useful import singleton

INIT_PRICE_VALUE = 0.0
INIT_VOLUME_VALUE = 0

INIT_STRING_VALUE = ''
INIT_DATETIME_VALUE = None
INIT_NONE_VALUE = None

class Constants(object):
    Buy = 'long'
    Sell = 'short'
    Open = 'open'
    Cover = 'cover'
    Close = 'close'
    ForceClose ='forceclose'
    CloseToday ='closetoday'
    CloseYesterday = 'closeyesterday'
    Long = 'long'
    Short = 'short'
    Idle = 'idle'

    ARB = 'ARB'  # 套利
    HEDGE = 'HEDGE' # 套保
    SPEC = 'SPEC'   # 投机

    class MarketOrder(object):
        A = 'A' #即时成交
        B = 'B' #最优5挡
        C = 'C' #全额成交
        D = 'D' # 本方最优价格
        E = 'E' # 对手最优价格

    class OrderStatus(object):
        Unknown= 0
        Auditing =      1  # 审批中
        AuditError =    2  # 审批失败
        Registered =    3  # 已报
        Pending_Dealing = 4     # 已报交易所，等待成交
        Rejected =      5       #  拒绝
        Pending_Cancel = 6      # 撤单，待交易所确认
        Cancelled =     7       # 撤单已完成
        Partial_Pending_Cancel = 8 # 部分成交，等待撤单中
        Partial_Cancelled = 9   # 部分成交，且撤单完成
        Partial_Filled = 10     # 部分成交
        Fully_Filled = 11       #  全部成交

    class KMarker(object):
        M1 = '1m'
        M5 = '5m'
        M15 = '15m'
        M30 = '30m'
        M60 = '60m'
        D = 'd'


# ------------------------------------------------------
class MarketGenerator(object):
    """行情数据生成器"""
    def __init__(self,market=None):
        self.market = market

    def init(self,*args,**kwargs):
        return self

    def open(self):
        pass

    def close(self):
        pass

    def getHistoryBars(self,code,cycle,limit,now=None):
        """取得历史k线
            now : 获取历史k线的截止日期
        """
        return []



class MarketRecorder(object):
    """行情记录器接口"""
    def write(self,obj):
        if isinstance(obj,TickData):
            pass

        if isinstance(obj,BarData):
            pass

    def init(self,*args,**kwargs):
        return self

    def open(self):
        pass

    def close(self):
        pass

class MarketFileRecorder(MarketRecorder):
    """文件系统存储"""
    def __init__(self,path='data'):
        MarketRecorder.__init__(self)
        self.path = path

    def write(self, obj):
        filename = ''
        if isinstance(obj,TickData):
            filename = '{}_{}.tick'.format(obj.code,current_date_string())
        if isinstance(obj,BarData):
            filename = '{}_{}_{}.bar'.format(obj.code,current_date_string(),obj.cycle)

        filepath = os.path.join(self.path,filename)
        text = obj.json()
        fp =  open(filepath,'a+')
        fp.write(text+'\n')
        fp.close()
        # print 'write record:'+filepath

    def open(self):
        pass

    def close(self):
        pass

class RedisRecorder(MarketRecorder):
    def __init__(self):
        MarketRecorder.__init__(self)
        self.redis = None

    def open(self):
        pass

    def close(self):
        pass


class TickData(object):
    """行情分时tick数据"""
    def __init__(self):
        self.code = None
        self.price = Price()

        self.trade_object = None
        self.sys_time = None  # 系统时间 datetime.datetime

    def dict(self):
        data = hash_object(self.price)
        data.update( hash_object(self,excludes=('trade_object','price')) )
        return data

    def json(self):
        data = self.dict()
        if data['time']:
            data['time'] = timestamp_to_str(datetime_to_timestamp(data['time']))
        if data['sys_time']:
            data['sys_time'] = timestamp_to_str(datetime_to_timestamp(data['sys_time']))
        return json.dumps(data)

    def assign(self,data):
        object_assign(self.price,data)
        object_assign(self,data)
        return self

class BarData(object):
    """行情k线数据"""
    def __init__(self):
        self.code = None        # 合约代码
        self.cycle = '1m'       # 周期 1m,5m,15m,30m
        self.open = 0
        self.close = 0
        self.high = 0
        self.low = 0
        self.vol = 0            # 成交量
        self.amount = 0         # 成交额
        self.time = None        # datetime.datetime
        self.sys_time = None     # 系统时间 datetime.datetime

        self.trade_object = None

    def dict(self):
        data = hash_object(self, excludes=('trade_object', ))
        return data

    def json(self):
        data = self.dict()
        # print data
        if data['time']:
            data['time'] = timestamp_to_str(datetime_to_timestamp(data['time']))
        if data['sys_time']:
            data['sys_time'] = timestamp_to_str(datetime_to_timestamp(data['sys_time']))
        return json.dumps(data)

    def assign(self,data):
        object_assign(self,data)
        return self


class BarDataEndFlag(BarData):
    """终止信号"""
    def __init__(self):
        BarData.__init__(self)

class AccountStat(object):
    """账户当前状态记录"""
    def __init__(self):
        self.time = 0
        self.usable_amount = 0  # 可用资金总额
        self.balance =0         # 资金余额
        self.frozen_amount = 0  # 冻结资金
        self.drawable_amount = 0 # 可取资金
        self.reference_value = 0 # 参考市值
        self.asset_amount = 0  # 总资产
        self.frozen_buy = 0      # 买入冻结
        self.frozen_sell = 0    # 卖出冻结




class Error(object):
    """错误信息"""
    def __init__(self):
        self.code = 0
        self.message = ''

    @property
    def empty(self):
        return self.code == 0

class AnyData(object):pass
# ------------------------------------------------------



class Price(object):
    """标的物价格"""
    def __init__(self):
        self.time = None
        self.last = 0  # 最新成交价
        self.qty = 0    # 成交数量
        self.amount = 0 # 成交金额

        self.total_qty = 0 # 总成交量
        self.total_amount = 0 # 总成交额

        self.yd_close = 0 # 昨日收盘价
        self.diff = 0       # 涨跌值
        self.diff_rate = 0  # 涨跌幅率

        self.sell_1 = 0
        self.sell_2 = 0
        self.sell_3 = 0
        self.sell_4 = 0
        self.sell_5 = 0
        self.sell_qty_1 = 0   # 量
        self.sell_qty_2 = 0   # 量
        self.sell_qty_3 = 0   # 量
        self.sell_qty_4 = 0   # 量
        self.sell_qty_5 = 0   # 量

        self.buy_1 = 0
        self.buy_2 = 0
        self.buy_3 = 0
        self.buy_4 = 0
        self.buy_5 = 0
        self.buy_qty_1 = 0   # 量
        self.buy_qty_2 = 0   # 量
        self.buy_qty_3 = 0   # 量
        self.buy_qty_4 = 0   # 量
        self.buy_qty_5 = 0   # 量

    def dict(self):
        return hash_object(self)

class ParamController(object):
    """策略运行参数控制器
    策略运行过程中对交易代码对象的参数设置和读取
    """
    def __init__(self):
        pass

    def get(self,strategy_id,**kwargs):
        """
        一次查询多个参数值 ,   { name=def_val, .. }
        kwargs is null , return all params
        """
        return {}

    def set(self,strategy_id,**kwargs):
        """一次设置多个值"""
        return self

    def get_code(self,strategy_id,name):
        return None

    def get_codes(self, strategy_id, all=False):
        """获取所有证券代码
         all = True ,所有包含已被禁用的
        """
        return []

    def set_code(self, strategy_id, code_name, **kwargs):
        """设置指定证券代码的多个参数值"""
        pass

    def get_entity(self,strategy_id,code_name,entity_id):
        return None

    def set_entity(self,strategy_id,code_name,entity_id,**kwargs):
        return self

class MongoParamController(ParamController):
    """策略运行参数控制器
    策略运行过程中对交易代码对象的参数设置和读取
    """
    def __init__(self,strategy=None):
        ParamController.__init__(self)
        self.conn = None

    def open(self,dbname='TradeFisher',host='127.0.0.1',port=27017):
        from pymongo import MongoClient
        from mantis.sg.fisher import model
        self.conn = MongoClient(host, port)
        model.set_database(self.conn[dbname])   # 策略名称为数据库名
        return self

    def close(self):
        self.conn.close()

    def get(self,strategy_id,**kwargs):
        """查询策略的参数配置
        一次查询多个参数值 ,   { name=def_val, .. }
        kwargs is null , return all params
        """
        from mantis.sg.fisher import model
        param = model.StrategyParam.get(strategy_id = strategy_id )
        return param

    def get_conn_url(self,conn_id):
        """获得交易连接信息"""
        from mantis.sg.fisher import model
        url = model.ConnectionUrl.get(id = conn_id)
        return url

    def set(self,strategy_id,**kwargs):
        """一次设置多个策略参数值"""
        from mantis.sg.fisher import model
        param = model.StrategyParam.get(strategy_id=strategy_id)
        if not param:
            param = model.StrategyParam()
            param.strategy_id = strategy_id
        param.assign(kwargs)
        param.save()
        return self

    def get_code(self,strategy_id,code_name):
        from mantis.sg.fisher import model
        code = model.CodeSettings.get(strategy_id=strategy_id,code = code_name)
        return code

    def get_codes(self,strategy_id,all=False):
        """获取所有证券代码
         all = True ,所有包含已被禁用的
        """
        from mantis.sg.fisher import model
        codes = model.CodeSettings.find(strategy_id = strategy_id)
        result = []
        for code in codes:
            if not all and code.enable == 0:
                continue
            result.append(code)
        return result

    def set_code(self,strategy_id,code_name,**kwargs):
        """设置指定证券代码的多个参数值"""
        from mantis.sg.fisher import model
        code = model.CodeSettings.get(strategy_id = strategy_id , code = code_name)
        if not code :
            code = model.CodeSettings()
            code.strategy_id = strategy_id
            code.code = code_name
        code.assign(kwargs)
        code.save()

    def get_entity(self,strategy_id,code_name,entity_id):
        from mantis.sg.fisher import model
        entity = model.EntitySettings.get(strategy_id = strategy_id, code = code_name , entity_id = entity_id)
        return entity

    def set_entity(self,strategy_id,code_name,entity_id,**kwargs):
        """设置证券代码的策略实体对象的多个参数值"""
        from mantis.sg.fisher import model
        entity = model.EntitySettings.get(strategy_id = strategy_id , code = code_name, entity_id = entity_id)
        if not entity :
            entity = model.EntitySettings()
            entity.strategy_id = strategy_id
            entity.code = code_name
            entity.entity_id = entity_id
        entity.assign(kwargs)
        entity.save()




class StrategySignal(object):
    """触发买卖信号信息"""
    def __init__(self,code='',text=''):
        self.code = code  # 证券代码
        self.text = ''  # 信号描述
        if isinstance(text, (tuple,list) ):
            for _ in text:
                self.text += ' '+ str(_)
        else:
            self.text = text

    def dict(self):
        return dict(code=self.code,text=self.text)


