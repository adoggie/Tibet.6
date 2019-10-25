#coding:utf-8

"""

ctp 行情和交易适配

*  ctp 行情从 redis 的pubsub通道直接订阅指定合约的tick和bar
* 交易接口从 ctptradeCXX 服务的http接口访问持仓、委托、资金信息，并通过其接口进行委托和撤单

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
from mantis.sg.fisher.utils.useful import singleton,object_assign,hash_object
from mantis.sg.fisher.utils.timeutils import timestamp_to_str
from mantis.sg.fisher import stbase,stutils
from mantis.fundamental.redis.broker import MessageBroker
from mantis.sg.fisher.stbase.futures import Price,BarData , \
    Position , TradeReturn , OrderRecord , AccountStat
from mantis.sg.fisher.stbase.controller import TradeController

class CtpMarket(stbase.Market):
    """行情接口"""
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
        # self.thread_quotes = threading.Thread(target=self.quotesThread)
        self.broker = MessageBroker()

    def init(self,*args, **kwargs ):
        """
        md_broker = "192.168.1.252:6379:0:",
        db_conn :  mongodb connection
        """
        self.logger = stbase.controller.getLogger()
        self.cfgs.update(kwargs)
        stbase.Market.init(self)
        md_broker = kwargs.get('md_broker')
        host,port,db,passwd = md_broker.split(':')
        port = int(port)
        db = int(db)
        self.broker.init(dict(host=host, port=port,db=db,password= passwd))

        return self

    def open(self):
        self.broker.open()
        stbase.Market.open(self)
        return True

    def quoteTickRecv(self,message,ctx):
        data = message
        tick = json.loads(data)
        dt = datetime.datetime.fromtimestamp(tick['Timestamp'])
        tick['DateTime'] = datetime.datetime.strptime(tick['DateTime'], '%Y%m%d %H:%M:%S.%f')
        tick['SaveTime'] = datetime.datetime.now()

        code =  tick['InstrumentID']
        data = stbase.TickData()
        data.code = code
        data.trade_object = stbase.controller.futures.getOrNewTradeObject(code)
        data.sys_time = datetime.datetime.now()

        price = Price()
        price.time = data.sys_time
        object_assign(price,tick)

        data.price = price
        data.trade_object.price = data.price

        self.putData(data)  # 置入处理队列等待线程读取

    def quoteBarRecv(self,message,ctx):
        data = message
        data = json.loads(data)

        ktype = '{}m'.format(data['cycle'])
        code = data['symbol']
        name = '{}-{}'.format(code, ktype)

        last = self.bar_last_data[name].get('last')

        # self.bar_last_data[name]['last'] = current
        bar = BarData()
        object_assign(bar,data,add_new=True)
        bar.cycle = ktype
        bar.code = code
        bar.time = datetime.datetime.strptime(data['datetime'], '%Y%m%d %H:%M:%S.%f')
        bar.sys_time = datetime.datetime.now()
        bar.trade_object = stbase.controller.futures.getTradeObject(code)
        self.putData(bar)  # 置入处理队列等待线程读取

    def close(self):
        stbase.Market.close(self)
        self.broker.close()
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
            object_assign(bar,r,add_new=True)
            result.append(bar)
        return result

    def getYdClosePrice(self,code):
        """查詢昨日 收盤價
         ? 如果盤后查詢，則取最後一根而不是倒數第二
        """
        stock = stbase.stocks.getTradeObject(code)
        return stock.yd_close
        # if not stutils.Stocks.in_trading_time():
        #     stbase.println(" not in trading time ..")
        #     return self.getHistoryBars(code,'d', 2,True)[-1].Close
        # return self.getHistoryBars(code,'d', 2)[-1].Close

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

        channelname = 'ctp.tick.pub_' + code
        channel = self.broker.createPubsubChannel( channelname, self.quoteTickRecv)
        channel.open()

        return stock

    def subBar(self,code,handler,cycle='1m'):
        """订阅不同周期的k线事件 , ctp.bar.pub_AP910_1m"""
        stock = stbase.Market.subBar(self, code, handler, cycle)
        self.bar_codes[cycle].append(code)
        name ='{}-{}'.format(code,cycle)
        self.bar_last_data[name] = {'last':None}

        name = '{}_{}'.format(code, cycle)
        channelname = 'ctp.bar.pub_' + name
        channel = self.broker.createPubsubChannel(channelname, self.quoteBarRecv)
        channel.open()

        return stock

    def requestFreshMarket(self,code):
        url = self.cfgs.get("td_api_url") + '/ctp/instrument/query'
        try:
            params = dict(instrument=code)
            res = requests.post(url, params)
            data = res.json().get('result', {})
        except:
            traceback.print_exc()

#市场	代码	活跃度	现价3	昨收	开盘	最高	最低7	保留	保留	总量10	现量11	总金额12	内盘13	外盘14	保留	保留	买一价17	卖一价	买一量	卖一量20	买二价	卖二价	买二量	卖二量	买三价25	卖三价	买三量	卖三量	买四价	卖四价30	买四量	卖四量	买五价	卖五价	买五量35	卖五量	保留	保留	保留	保留40	保留	涨速	活跃度43
#0	002517	3201	4.980000	5.070000	5.080000	5.080000	4.840000	14330103	-498	481362	37	238152352.000000	286382	194980	-1	10460	4.980000	4.990000	614	1192	4.970000	5.000000	2051	2672	4.960000	5.010000	1976	3221	4.950000	5.020000	1312	2015	4.940000	5.030000	430	1547	1593	0	30	24	-1	0.610000	3201

    def on_tick(self, qs):
        """行情进入，生成 TickData()对象，推送到 stbase.Market的处理工作队列
            主动查询需要控制tick上报时消重
        """

        code = qs[1]

        last = self.tick_codes[code].get('last')
        current = ','.join(qs)
        if last == current:
            # print 'duplicated tick.'
            return
        self.tick_codes[code]['last'] = current

        vs = map(float, qs)
        data = stbase.TickData()
        data.code = code
        data.trade_object = stbase.stocks.getOrNewTradeObject(code)
        data.sys_time = datetime.datetime.now()

        price = data.price
        price.time = data.sys_time

        price.last = vs[3]
        price.yd_close = vs[4]
        price.qty = vs[11]
        price.amount =  0
        price.total_qty = vs[10]
        price.total_amount = vs[12]
        price.diff = price.last - price.yd_close  # 当前价差
        price.diff_rate = price.diff/(price.yd_close*1.0)
        price.sell_1 =  vs[18]
        price.sell_2 =  vs[22]
        price.sell_3 = vs[26]
        price.sell_4 = vs[30]
        price.sell_5 = vs[34]
        price.sell_qty_1 = vs[20]
        price.sell_qty_2 = vs[24]
        price.sell_qty_3 = vs[28]
        price.sell_qty_4 = vs[32]
        price.sell_qty_5 = vs[36]

        price.buy_1 = vs[17]
        price.buy_2 = vs[21]
        price.buy_3 = vs[25]
        price.buy_4 = vs[29]
        price.buy_5 = vs[33]

        price.buy_qty_1 = vs[19]
        price.buy_qty_2 = vs[23]
        price.buy_qty_3 = vs[27]
        price.buy_qty_4 = vs[31]
        price.buy_qty_5 = vs[35]

        data.trade_object.price = data.price

        self.putData(data)          # 置入处理队列等待线程读取

    def barWrapped(self,code,cycle,kdata):
        name = '{}-{}'.format(code, cycle)
        last = self.bar_last_data[name].get('last')
        current = ','.join(kdata)
        if last == current:
            return
        self.bar_last_data[name]['last'] = current

        dt = kdata[0]
        dt = parse(dt)

        nums = kdata[1:]

        nums = map(float, nums)

        data = stbase.BarData()
        data.amount = nums[5]
        data.open = nums[0]
        data.high = nums[2]
        data.low = nums[3]
        data.close = nums[1]
        data.vol = nums[4]

        data.time = dt
        data.sys_time = datetime.datetime.now()
        data.code = code
        data.trade_object = stbase.stocks.getTradeObject(code)

        data.cycle = cycle
        return data

    def on_bar(self,code,cycle,kdata):
        """k线数据触发, 消重处理"""

        # data.num = num      # bar的最大流水
        data = self.barWrapped(code,cycle,kdata)
        self.putData(data)


class CtpTrader(stbase.Trader):
    """交易接口"""
    def __init__(self):
        stbase.Trader.__init__(self)
        # self.trade_conn = None  # 交易通道
        self.logger = None
        self.cfgs = {'query_freq': 1}
        self.thread_query = threading.Thread(target=self.queryThread)
        self.actived = False
        self.position_list = {}  # 持仓记录

        self.orders = OrderedDict()       # 委托中的订单 { user_order_id : order, .. }
        self.trades = OrderedDict()     #{order_id:[tr,..] , .. }  一个委托单存在多个成交记录
        self.broker = MessageBroker()

    def init(self,*args,**kwargs):
        """
        td_api_url : http://host:port/ctp  [ http ]

        td_stream : 192.168.1.12:7700    [ tcp ]  目前未启用，可能采用reids 的pub/sub替代接收推送来的通知
        """
        self.stat = AccountStat()
        self.logger = stbase.controller.getLogger()
        self.cfgs.update(kwargs)
        stbase.Trader.init(self,**kwargs)

        md_broker = kwargs.get('md_broker')
        host, port, db, passwd = md_broker.split(':')
        port = int(port)
        db = int(db)
        self.broker.init(dict(host=host, port=port, db=db, password=passwd))

        return self

    def open(self):
        self.broker.open()
        pubsub_event_name = self.cfgs.get('pubsub_event_name')
        channel = self.broker.createPubsubChannel(pubsub_event_name, self.eventRecv)
        channel.open()

        stbase.Trader.open(self)
        self.thread_query.start()
        return True

    def close(self):
        self.actived = False
        self.broker.close()
        # self.thread_query.join()

    def eventRecv(self,data,ctx):
        """ctpTradeCxx 推送过来的 委托和成交事件
        event : 'event_order' , 'event_trade'
        """
        from mantis.sg.fisher.model import model
        from mantis.sg.fisher.ctp.errors import error_defs

        message = json.loads(data)
        event = message["event"]
        print event
        if event == "event_order":  # 处理委托通知
            order = OrderRecord()
            object_assign(order, message)
            order.normalize()
            self.orders[order.user_order_id] = order

            log = model.StrategyOrderLog()
            log.strategy_id = self.cfgs.get('strategy_id')
            object_assign(log,hash_object(order),True )
            log.save()
        elif event == "event_trade":
            tr = TradeReturn()
            object_assign(tr, message)
            tr.normalize()

            log = model.StrategyTradeLog()
            log.strategy_id = self.cfgs.get('strategy_id')
            object_assign(log, hash_object(tr),True )
            log.save()
        elif event == "event_error":
            log = model.StrategyErrorLog()
            log.strategy_id = self.cfgs.get('strategy_id')
            object_assign(log, message, True)
            errcode = message.get('errcode',0)
            errmsg = error_defs.get(int(errcode),'')
            log.detail = errmsg

            log.save()


    def wait_for_shutdown(self,inf = 1000*1000):
        time.sleep(inf)

    def connectServer(self):
        pass

    def queryThread(self):
        """查询持仓、资金、委托
        仅执行 委托、成交 一次查询 ； 资金、持仓连续查询
        """
        self.actived = True
        freqs = self.cfgs.get('query_freq')

        orders = self._getOrders()
        for order in orders:
            self.orders[order.user_order_id] = order

        trades = self._getTradeRecords()
        for tr in trades:
            if not self.trades.has_key(tr.order_id):
                self.trades[tr.order_id] = []
            self.trades[tr.order_id].append(tr)

        while self.actived:
            time.sleep(freqs)
            try:
                self.queryDatas()
            except:
                self.logger.error(traceback.print_exc())
        self.logger.debug('Ctp Trader Query Thread Exiting..')


    def queryDatas(self):
        """
        查询各类持仓、订单、委托等信息
        :return:
        """
        self.query_resp_funds()

    def query_resp_funds(self):
        """资金返回"""
        url = self.cfgs.get("td_api_url") + '/ctp/account'
        try:
            res = requests.get(url,timeout=3.)
            data = res.json().get('result', {})
            self.stat = AccountStat()
            object_assign( self.stat, data)
            self.stat.normalize()
        except:
            self.logger.error("Request Trader Service Fail Down.")
            # traceback.print_exc()

    def getAccountStat(self):
        return self.stat

    # def onRtsChanged(self,rts_list):
    #     """委托或成交回报"""
    #     fmt = '%Y-%m-%d %H:%M:%S'
    #     tr_list = []
    #     for _ in rts_list:
    #
    #         tr = stbase.TradeReturn()
    #         tr.type = _.Type
    #         tr.order_id = _.OrigSerialNo
    #         tr.user_id = _.OrigSource
    #         tr.protfolio_num = _.PortfolioNum
    #         tr.code = _.ServerCode
    #         tr.direction = stbase.Constants.Buy
    #         if _.BSType == 'S':
    #             tr.direction = stbase.Constants.Sell
    #
    #         tr.oc = stbase.Constants.Open
    #         if _.OCFlag == 'C':
    #             tr.oc = stbase.Constants.Cover
    #         tr.order_price = _.OrderPrice
    #         tr.order_qty = _.OrderQty
    #
    #
    #         # print _.OrderTime,type(_.OrderTime)
    #         if _.OrderTime:
    #             tr.order_time = datetime.datetime.fromtimestamp(_.OrderTime)
    #         if _.KnockTime:
    #             tr.knock_time = datetime.datetime.fromtimestamp(_.KnockTime)
    #         tr.knock_code = _.KnockCode
    #         tr.knock_price = _.KnockPrice
    #         tr.knock_qty = _.KnockQty
    #         tr.knock_amount = _.KnockAmt
    #         tr.total_withdraw_qty = _.TotalWithdrawQty
    #         tr.total_knock_qty = _.TotalKnockQty
    #         tr.total_knock_amount = _.TotalKnockAmt
    #         tr.status = stbase.Constants.OrderStatus.Unknown
    #
    #         if _.StatusCode == 'Registered':
    #             tr.status = stbase.Constants.OrderStatus.Registered
    #         elif _.StatusCode == 'Pending_Dealing':
    #             tr.status = stbase.Constants.OrderStatus.Pending_Dealing
    #         elif _.StatusCode == 'Rejected':
    #             tr.status = stbase.Constants.OrderStatus.Rejected
    #         elif _.StatusCode == 'Pending_Cancel':
    #             tr.status = stbase.Constants.OrderStatus.Pending_Cancel
    #         elif _.StatusCode == 'Cancelled':
    #             tr.status = stbase.Constants.OrderStatus.Cancelled
    #         elif _.StatusCode == 'Partially_Pending_Cancel':
    #             tr.status = stbase.Constants.OrderStatus.Partial_Pending_Cancel
    #         elif _.StatusCode == 'Partially_Cancelled':
    #             tr.status = stbase.Constants.OrderStatus.Partial_Cancelled
    #         elif _.StatusCode == 'Partially_Filled':
    #             tr.status = stbase.Constants.OrderStatus.Partial_Filled
    #         elif _.StatusCode == 'Fully_Filled':
    #             tr.status = stbase.Constants.OrderStatus.Fully_Filled
    #         elif _.StatusCode == 'Auditing':
    #             tr.status = stbase.Constants.OrderStatus.Auditing
    #         elif _.StatusCode == 'AuditError':
    #             tr.status = stbase.Constants.OrderStatus.AuditError
    #
    #         tr_list.append(tr)
    #
    #     stbase.Trader.onRtsChanged(self, tr_list)
        # stbase.println('onRtsChanged(), size:%s'%(len(rts_list)))

    def onPositionChanged(self):
        # 持仓和资金变更通知
        stbase.Trader.onPositionChanged(self)
        # stbase.println('onPositionChanged() , ')

    def get_gddm(self,code):
        """获得股东代码"""
        return ''

    def sendOrder(self, order_req = stbase.OrderRequest(code='')):
        """发送订单
            :param: order_req : stbase.OrderRequest
        """
        # 0 买入
        # 1 卖出
        Buy = "buy"
        Sell = "sell"
        direction = Buy
        if order_req.direction == stbase.Constants.Sell:
            direction = Sell
        # print order_req.dict()
        oc = "open"
        if order_req.oc in (stbase.Constants.Cover,stbase.Constants.Close):
            oc = "close"
        if order_req.oc == stbase.Constants.ForceClose:
            oc ="forceclose"
        if order_req.oc == stbase.Constants.CloseToday:
            oc = 'closetoday'
        if order_req.oc == stbase.Constants.CloseYesterday:
            oc = 'closeyesterday'

        url = self.cfgs.get("td_api_url") + '/ctp/order/send'

        order_id = ''
        cc = stbase.futures.Constants.ContingentConditionType.Immediately
        tc = stbase.futures.Constants.TimeConditionType.IOC
        vc = stbase.futures.Constants.VolumeConditionType.VC_CV

        cc = order_req.opts.get('cc',cc)
        tc = order_req.opts.get('tc',tc)
        vc = order_req.opts.get('vc',vc)

        try:
            data = dict( instrument = order_req.code,
                        price = order_req.price,
                         volume = order_req.quantity,
                        direction = direction,
                        oc = oc,
                         price_type = order_req.price_type,
                        exchange_id = order_req.exchange_id,
                         cc = cc ,
                         tc = tc ,
                         vc = vc
                         )

            res = requests.post(url,data)
            order_id = res.json().get('result')
        except:
            traceback.print_exc()
        return order_id

    def get_code_by_order_id(self,order_id):
        """查询委托单的证券代码"""
        order = self.orders.get(order_id)
        if order:
            return order.code
        else:
            print self.orders
        return ''


    def _cancelOrder(self,order_id):
        """撤销订单"""
        url = self.cfgs.get("td_api_url") + '/ctp/order/cancel'
        try:
            data = dict(order_id = order_id)
            res = requests.post(url, data)
            order_id = res.json().get('result')
        except:
            traceback.print_exc()
        return None

    def cancelOrder(self,order_id,timeout=5):
        """撤销订单
            order_id :  user_order_id
        """
        for _ in range(timeout):
            order = self.orders.get(order_id)
            if order:
                self._cancelOrder(order.order_id)
                break
            time.sleep(1)


    def getPosition(self,code='',strategy_id='',direction=''):
        """查询指定 代码或者指定策略的持仓记录"""
        url = self.cfgs.get("td_api_url") + '/ctp/position/list'
        result = []
        try:
            res = requests.get(url,timeout=3)
            values = res.json().get('result', [])
            if not values:
                values = []
            for _ in values:
                pos = Position()
                object_assign(pos, _)
                okay = pos
                if code:
                    if code != pos.InstrumentID:
                        okay = None
                if okay and direction:
                    if direction == stbase.Constants.Buy and pos.PosiDirection != stbase.futures.Constants.PositionDirection.Long:
                        okay = None
                    if direction == stbase.Constants.Sell and pos.PosiDirection != stbase.futures.Constants.PositionDirection.Short:
                        okay = None
                if okay:
                    result.append(pos)

        except:
            traceback.print_exc()
        return result

    def _getOrders(self,order_id='',code='',strategy_id=''):
        """查询委托信息，状态包括： 未成、部分成、全成、错误
            strategy_id 作为 委托的 orign source  字段
        """

        url = self.cfgs.get("td_api_url") + '/ctp/order/list'
        orders = []
        try:
            res = requests.get(url,timeout=3)
            values = res.json().get('result',[])
            if not values:
                values =[]
            for _ in values:
                order = OrderRecord()
                object_assign(order,_)
                order.normalize()
                if order_id:
                    if order_id in ( order.order_id, order.user_order_id):
                        orders.append(order)
                else:
                    orders.append(order)
        except:
            traceback.print_exc()
        return orders

    def getOrders(self,order_id='',code='',strategy_id=''):
        """查询委托信息，状态包括： 未成、部分成、全成、错误
            strategy_id 作为 委托的 orign source  字段
        """
        orders  = []
        for _,order in self.orders.items():

            if order_id:
                if order_id in ( order.order_id, order.user_order_id):
                    orders.append(order)
            else:
                orders.append(order)
        return orders

    def waitOrder(self,user_order_id,timeout=1):
        """等待委托完成
        :return: 成交数量
        """
        traded_num = 0  # 成交数量
        for _ in range(timeout*2):
            order = self.orders.get(user_order_id,None)
            if order:
                traded_num = order.VolumeTraded
                if not order.cancelable():
                    break
                # trades =  self.trades.get(order.order_id,[])
                # for tr in trades:
                #     traded_num += tr.Volume
                # if traded_num >= order.
            time.sleep(.5)
        return traded_num


    def _getTradeRecords(self):
        url = self.cfgs.get("td_api_url") + '/ctp/trade/list'
        orders = []
        try:
            res = requests.get(url,timeout=3)
            values = res.json().get('result',[])
            if not values:
                values =[]
            for _ in values:
                tr = TradeReturn()
                object_assign(tr,_)
                tr.normalize()

                orders.append(tr)
        except:
            traceback.print_exc()
        return orders


    def getTradeRecords(self, order_id_ ):

        trades = self.trades.get( order_id_ ,[])
        return trades


    def getAmountUsable(self):
        """账户可用资金"""
        return self.stat.Available

    def getAmountAsset(self):
        """现货总资产"""
        return self.stat.Balance

