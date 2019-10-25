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

from base import *
from logger import *
from controller import *
import base

class Strategy(object):
    """策略基类"""
    CODES=['0600000']
    TICKS= CODES
    BARS={'1m':CODES,'5m':CODES,'15m':CODES,'30m':[],'60m':[],'d':[]}

    class Runnable(object):
        RUN = 1
        STOP = 0
    def __init__(self,name,product):
        self.name = name
        self.product = product
        self.logger = StragetyLogger(self)      # 默认日志输出
        self.any = AnyData()
        self.start_time = None      # 启动时间
        self.trading_codes = {} # { code:{allow:True,start:xxx } }
        self.cfgs = {}
        self.mg_conn = None     # mongodb connection
        # self.param_controller = ParamController(self)
        self.entities = OrderedDict()   # { code: entity }
        self.timer_handlers = OrderedDict() # {'code-1': handler}  证券代码 + 间隔秒数 对应 定时器函数
        self.risk_manager = None    # 風險管理
        self.loader = None

        self.broker = None
        self.pub_log_message = None  # 日志消息
        self.pub_log_trade = None  # 交易信号
        self.running = False

    def init(self,*args,**kwargs):
        # name = os.path.join( TradeController().data_path,self.name)
        name = self.name
        self.logger.addAppender(FileLogAppender(name).open())
        self.cfgs.update(kwargs)
        return self

    def setLoader(self,loader):
        self.loader = loader
        return self

    @property
    def market(self):
        return self.product.market

    @property
    def trader(self):
        return self.product.trader

    @property
    def id(self):
        return self.name

    def subTick(self,code):
        """订阅分时tick"""
        if self.product.market:
            self.product.market.subTick(code,handler=self.onTick)
        return self

    def batchSubTicks(self,codes):
        for code in codes:
            self.subTick(code )
        return self

    def subBar(self,code,bar='1m'):
        """订阅k线"""
        if self.product.market:
            self.product.market.subBar(code,self.onBar,bar)
        else:
            print 'market not be set..'
        return self

    def setLogger(self,logger):
        """设置策略日志对象"""
        self.logger = logger
        return self

    def getLogger(self):
        return self.logger

    def onTick(self,tick):
        entity = self.entities.get(tick.code)
        if entity and entity.trigger == 'tick':
            entity.onTick(tick)

    def onBar(self,bar):
        entity = self.entities.get(bar.code)
        if entity and entity.trigger == 'bar':
            entity.onBar(bar)

    def getSubTickCodes(self):
        """
        获取订阅tick的合约代码， 可覆盖
        :return:
        """
        result = []
        codes = TradeController().getParamController().get_codes(self.id)
        for _ in codes:
            if _.sub_tick:
                result.append(_.code)
        return result

    def getSubBarCodes(self):
        """
        获取订阅bar的合约代码, 可覆盖
        :return:
         {'1m':[code,...] }
        """
        BARS = {Constants.KMarker.M1: [],
                Constants.KMarker.M5: [],
                Constants.KMarker.M15: [],
                Constants.KMarker.M30: [],
                Constants.KMarker.M60: [],
                Constants.KMarker.D: []}

        result = []
        codes = TradeController().getParamController().get_codes(self.id)
        for _ in codes:
            if _.sub_bar_1m : BARS[Constants.KMarker.M1].append( _.code )
            if _.sub_bar_5m : BARS[Constants.KMarker.M5].append( _.code )
            if _.sub_bar_15m : BARS[Constants.KMarker.M15].append( _.code )
            if _.sub_bar_30m : BARS[Constants.KMarker.M30].append( _.code )
            if _.sub_bar_60m : BARS[Constants.KMarker.M60].append( _.code )

        return BARS

    def start(self):
        """策略启动
        1. 初始化所有证券代码，读取证券代码对应要加载的策略算法对象(entity)
        2.订阅所有预定的证券代码
        """

        # 1 -
        # from  mantis.sg.fisher.strepo import initialEntity
        # codes = TradeController().getParamController().get_codes(self.id)
        # for code in codes:
        #     entity = initialEntity(code.entity_id , self)
        #     if entity:
        #         self.entities[code.code] = entity
        #         # 处理定时器
        #         if entity.trigger == 'timer' and entity.timer_interval:
        #             name = '{}-{}'.format(code.code, entity.timer_interval)
        #             handler = self.onEntityTimer
        #             self.timer_handlers[name] = handler
        #             self.startTimer(handler,user=code.code,timeout = entity.timer_interval)

        self.running = True
        # 2 -
        for code in self.getSubTickCodes():
            self.subTick(code)
        for cycle,codes in self.getSubBarCodes().items():
            for code in codes:
                self.subBar(code,cycle)

        self.start_time = datetime.datetime.now()
        # self.logger.info('strategy:{} start..'.format(self.name))
        self.set_params(start_time = self.start_time,up_time = self.start_time)  # 记录启动时间
        self.startTimer(back=self.updateTime,timeout=1)

    def stop(self):
        """停止策略运行"""
        self.running = False
        self.logger.close()
        if self.mg_conn:
            self.mg_conn.close()

    def updateTime(self,timer):
        """记录策略有效时间"""
        if not self.running:
            return
        self.set_params(up_time = datetime.datetime.now())
        timer.start()

    def onEntityTimer(self,timer):
        code = timer.user
        timeout = timer.timeout

        entity = self.entities.get(code)
        if entity :
            entity.onTimer(timer)

    def startTimer(self,back=None,user=None,timeout = 1):
        """启动定时器，默认回调触发 self.onTimer"""
        if not back:
            back = self.onTimer
        TradeController().startTimer(back,user,timeout)

    def getAccountStat(self):
        return self.product.trader.getAccountStat()

    def getPosition(self,code='',strategy_id='' , direction = ''):
        """查询指定 本策略相关的持仓记录"""
        return self.product.trader.getPosition(code,strategy_id , direction)

    def getOrders(self,order_id='',code='',strategy_id=''):
        """查询委托信息，状态包括： 未成、部分成、全成、错误
            strategy_id 作为 委托的 orign source  字段
        """
        return self.product.trader.getOrders(order_id,code,self.name)

    def getTradeRecords(self):
        return self.product.trader.getTradeRecords()

    def buy(self,code,price,num,oc = Constants.Open , price_type='',exchange_id='', msg='',**opts):
        """默认买开,行为 msg 写入日志
        **opts:
          cc : ContingentCondition
          tc : TimeCondition
          vc : VolumeCondition
        """
        req = OrderRequest(code, price, num, Constants.Buy)
        req.oc = oc
        req.price_type = price_type
        req.exchange_id = exchange_id
        req.opts = opts
        order_id = self.product.trader.sendOrder(req)
        req.message = msg
        self.logger.orderRequest(req)
        req.order_id = order_id
        return  order_id

    def sell(self,code,price,num,oc = Constants.Open ,price_type='', exchange_id='',msg='',**opts):
        """默认卖开"""
        req = OrderRequest(code, price, num, Constants.Sell)
        req.oc = oc
        req.price_type = price_type
        req.exchange_id = exchange_id
        req.opts = opts
        order_id = self.product.trader.sendOrder(req)
        req.message = msg
        self.logger.orderRequest(req)
        req.order_id = order_id
        return order_id

    def cancelOrder(self,order_id):
        self.product.trader.cancelOrder(order_id)
        code = ''
        orders = self.getOrders(order_id)
        if orders:
            code = orders[0].code
        self.logger.orderCancel(code,order_id)

    def onPositionChanged(self):
        """持仓或资金变动事件"""
        pass

    def onRtsChanged(self, rts_list):
        pass

    def isTrading(self,code):
        """ 判别证券代码是否允许交易 ， 在控制管理端会暂停和停止证券的交易行为
            必须认为指定为可交易状态
        """
        cfg = self.trading_codes.get(code, {'allow': False, 'start': 0})
        return cfg['allow']

    def setTrading(self,code,allow=True):
        """指定证券代码进入可交易状态"""
        cfg = self.trading_codes.get(code,{'allow':False,'start':0})
        cfg['allow'] = allow
        if not allow :
            cfg['start'] = 0
        else:
            cfg['start'] = timestamp_current()

    def prepareDataEnv(self):
        """读取策略配置"""
        from pymongo import MongoClient
        from mantis.sg.fisher import model
        host = self.cfgs.get('host','127.0.0.1')
        port = self.cfgs.get('port',27017)
        self.mg_conn = MongoClient(host, port)
        model.database = self.mg_conn[self.name] # 策略名称为数据库名

    # def setParamController(self,controller):
    #     """设置证券产品运行控制器"""
    #     self.param_controller = controller
    #     controller.strategy = self
    #     return self

    def get_params(self):
        """
        查询策略设置相关参数
        :return:  model::StrategyParam
        """
        return TradeController().getParamController().get(self.id)

    getParams = get_params

    def set_params(self,**kwargs):
        """
        设置策略运行参数
        :param kwargs:
        :return:
        """
        return TradeController().getParamController().set(self.id,**kwargs)

    setParams = set_params

    def get_codes(self):
        """
        查询策略相关的多个交易证券代码对象
        :return:
        """
        return TradeController().getParamController().get_codes(self.id,True)

    getCodes = get_codes

    def get_code_params(self,code_name):
        """查询交易代码对象的运行参数设置"""
        return TradeController().getParamController().get_code(self.id,code_name)

    getCodeParams = get_code_params

    def set_code_params(self,code_name,**kwargs):
        """设置策略相关的证券交易代码对象的参数"""
        return TradeController().getParamController().set_code(self.id,code_name,**kwargs)

    setCodeParams = set_code_params

    def get_entity_params(self,code_name,entity_id):
        """返回算法实体对象的参数"""
        return TradeController().getParamController().get_entity(self.id,code_name,entity_id)

    def set_entity_params(self,strategy_id,code_name,entity_id,**kwargs):
        return TradeController().getParamController().set_entity(self.id,code_name,entity_id,**kwargs)

    def getParamController(self):
        return TradeController().getParamController()


    def is_code_enable(self,code):
        """返回當前證券代碼是否在交易狀態"""
        param = self.get_code_params(code)
        return param.enable == 1

    isCodeEnable = is_code_enable