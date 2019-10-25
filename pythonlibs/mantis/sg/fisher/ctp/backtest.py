#coding:utf-8

"""

ctp 行情和交易适配

* 模拟生成回测历史数据

直接从mongodb 读取 历史k线数据
"""

"""
量化技术指标计算 
https://github.com/QUANTAXIS/QUANTAXIS/blob/master/QUANTAXIS/QAData/base_datastruct.py

"""
import copy
import json
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse
import requests

from mantis.sg.fisher.utils.importutils import import_module,import_class
from mantis.sg.fisher.utils.useful import singleton,object_assign
from mantis.sg.fisher.utils.timeutils import timestamp_to_str
from mantis.sg.fisher import stbase,stutils
from mantis.fundamental.redis.broker import MessageBroker
from mantis.sg.fisher.stbase.futures import Price,BarData , \
    Position , TradeReturn , OrderRecord , AccountStat
from mantis.sg.fisher.stbase.base import BarDataEndFlag

class CtpMarketBarBackTest(stbase.Market):
    """回测行情接口(k线)"""
    def __init__(self):

        self.hq_conn = None
        stbase.Market.__init__(self, None)
        self.logger = None

        self.cfgs = { 'query_freq':.5}
        # self.cfgs.update(TDX_CFGS)

        self.tick_codes = {}  # {code:{last:???} }
        self.bar_last_data = {} # { code-cycle:??? } 消重处理，记录最新的一条bar记录
        self.bar_codes= {
            "1m":[],
            "5m":[],
            "15m":[],
            "30m":[],
            "60m":[],
            "d":[]
        }
        # self.codes =[] # 订阅的股票列表
        self.thread_bar = threading.Thread(target=self.quoteBarRecv)


    def init(self,*args, **kwargs ):
        """
        cycle : k线类型  1,5,15,30 ,..
        start : 开始时间
        end : 结束时间
        symbol : 合约名称
        db_conn :  mongodb connection
        freq : 0.5 读取频率
        """
        self.logger = stbase.controller.getLogger()
        self.cfgs.update(kwargs)
        stbase.Market.init(self)

        return self

    def open(self):
        stbase.Market.open(self)
        self.thread_bar.start()
        return True

    def quoteBarRecv(self):
        """一次读取指定条件的k线记录，并开始回放"""
        symbol = self.cfgs.get('symbol')
        cycle =self.cfgs.get('cycle')
        freq = self.cfgs.get('freq',0.5)

        db = self.cfgs.get('db_conn')['Ctp_Bar_{}'.format(cycle)]
        coll = db[symbol]

        wait = self.cfgs.get('wait',1)
        print 'wait for ',wait, 'seconds ..'
        time.sleep(wait)

        start = self.cfgs.get('start')
        end = self.cfgs.get('end')
        if isinstance(start,(str,unicode)):
            start = parse(start)
        if not end:
            end = datetime.datetime.now()
        else:
            end = parse(end)

        rs = coll.find({'datetime':{'$gte':start,'$lte':end }}).sort('datetime',1)
        # rs = coll.find().sort('datetime',1).limit(10)
        for data in list(rs):
            if freq:
                time.sleep(freq)

            bar = BarData()
            object_assign(bar,data,add_new=True)
            # ktype = '{}m'.format(data['cycle'])
            if cycle in ('D','d'):
                bar.cycle = cycle
            else:
                bar.cycle = '{}m'.format(cycle)     # 必须是 sc1907-1m 的格式
            bar.code = symbol
            bar.time = data['datetime']
            bar.sys_time = datetime.datetime.now()
            bar.trade_object = stbase.controller.futures.getTradeObject(symbol)
            self.putData(bar)  # 置入处理队列等待线程读取

        endflag = BarDataEndFlag()
        endflag.code  = symbol
        if cycle in ('D', 'd'):
            endflag.cycle = cycle
        else:
            endflag.cycle = '{}m'.format(cycle)
        self.putData(endflag)

    def close(self):
        stbase.Market.close(self)
        # self.thread_quotes.join()

    def tickInit(self, tick):
        tick.trade_object.price = tick.price
        tick.trade_object.max_price = tick.price.UpperLimitPrice
        tick.trade_object.min_price = tick.price.LowerLimitPrice

    def initTradeObject(self,tobj):
        """

        :param stock:  stbase.TradeObject
        :return:
        """
        from mantis.sg.fisher.stbase.futures import Position,Price
        # 初始化股票的初始参数， 交易限价、手续费等等
        if tobj.inited:
            return
        tobj.price = Price()
        tobj.pos = Position()

        tobj.inited = True
        return tobj

    def getHistoryBars(self,code,cycle='1m',limit=100,lasttime=None,inc_last=False):
        """获取历史k线
        剔除最后一根活动k线(盘中不能使用最后一根k线，或许是未完成计算的中间结果)
        result 以时间升序排列
        """
        from mantis.sg.fisher.stbase.futures import BarData
        result = [] # stbase.BarData()
        stock= self.product.getOrNewTradeObject(code)

        cycle_cat_map = {
            '1m': 1,'5m': 5,'15m': 15,
            '30m': 30,'60m': 60,'d': 'd'
        }

        scale = cycle_cat_map[cycle]
        db_conn = self.cfgs.get('db_conn')
        if not db_conn:
            return []
        dbname = 'Ctp_Bar_'+str(scale)
        coll = db_conn[dbname][code]
        if lasttime:
            if isinstance(lasttime,str):
                lasttime = parse(lasttime)
            rs = coll.find({'datetime':{'$lte':lasttime}}).sort( 'datetime',-1).limit(limit)
        else:
            rs = coll.find().sort( 'datetime',-1 ).limit(limit)

        rs = list(rs)
        rs.reverse()
        result = []
        for r in list(rs):
            bar = BarData()
            r['time'] = r['datetime']
            object_assign(bar,r,add_new=True)
            result.append(bar)
        return result


    def subReset(self):
        stbase.Market.subReset(self)
        self.tick_codes = {}
        self.bar_codes = {
            "1m":[],
            "5m":[],
            "15m":[],
            "30m":[],
            "60m":[],
            "d":[]
        }
        self.bar_last_data = {}
        return self

    def subTick(self, code, handler):
        """订阅分时行情"""
        stock = stbase.Market.subTick(self, code, handler)
        self.tick_codes[code]= {'last':None}
        return stock

    def subBar(self,code,handler,cycle='1m'):
        """订阅不同周期的k线事件 , ctp.bar.pub_AP910_1m"""
        stock = stbase.Market.subBar(self, code, handler, cycle)
        self.bar_codes[cycle].append(code)
        name ='{}-{}'.format(code,cycle)
        self.bar_last_data[name] = {'last':None}

        return stock

    def loadHistBars(self,*args,**kwargs):
        cfgs = {}
        cfgs.update(self.cfgs)
        cfgs.update(kwargs)

        symbol = cfgs.get('symbol')
        cycle = cfgs.get('cycle')
        freq = cfgs.get('freq', 0.5)
        dataset = cfgs.get('dataset')

        db = cfgs.get('db_conn')['Ctp_Bar_{}'.format(cycle)]
        coll = db[dataset]

        start = cfgs.get('start')
        end = cfgs.get('end')
        if isinstance(start, (str, unicode)):
            start = parse(start)
        if not end:
            end = datetime.datetime.now()
        else:
            end = parse(end)

        rs = coll.find({'datetime': {'$gte': start, '$lte': end}}).sort('datetime', 1)
        bars =[]
        for data in list(rs):
            bar = BarData()
            object_assign(bar, data, add_new=True)
            if cycle in ('D', 'd'):
                bar.cycle = cycle
            else:
                bar.cycle = '{}m'.format(cycle)  # 必须是 sc1907-1m 的格式
            bar.code = symbol
            bar.time = data['datetime']
            bar.sys_time = datetime.datetime.now()
            # bar.trade_object = stbase.controller.futures.getTradeObject(symbol)
            # self.putData(bar)  # 置入处理队列等待线程读取
            bars.append(bar)
        return bars


class CtpTraderBackTest(stbase.Trader):
    """回测模拟交易接口"""

    def __init__(self):
        self.cfgs = {}
        self.actived = False
        stbase.Trader.__init__(self)

    def init(self,*args,**kwargs):

        self.cfgs.update(kwargs)
        stbase.Trader.init(self,**kwargs)
        return self

    def open(self):
        stbase.Trader.open(self)
        return True

    def close(self):
        self.actived = False


    def sendOrder(self, order_req = stbase.OrderRequest(code='')):
        """发送订单
            :param: order_req : stbase.OrderRequest
        """
        return ''

    def cancelOrder(self,order_id):
        """撤销订单"""
        return ''


    def getPosition(self,code='',strategy_id='',direction=''):
        """查询指定 代码或者指定策略的持仓记录"""
        pass

    def getOrders(self,order_id='',code='',strategy_id=''):
        pass


    def getTrades(self):
        pass

    def getAmountUsable(self):
        """账户可用资金"""
        return 0

    def getAmountAsset(self):
        """现货总资产"""
        return 0

