#coding:utf-8

"""

tradex 行情和交易适配
"""

"""
量化技术指标计算 
https://github.com/QUANTAXIS/QUANTAXIS/blob/master/QUANTAXIS/QAData/base_datastruct.py

"""
import copy
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse

from mantis.sg.fisher.utils.importutils import import_module,import_class
from mantis.sg.fisher.utils.useful import singleton
from mantis.sg.fisher.utils.timeutils import timestamp_to_str
from mantis.sg.fisher import stbase,stutils

import TradeX2

#
# TDX_CFGS = dict(
#                 qsid = 36,
#                 host = "222.173.22.53",
#                 port = 7700,
#                 version = "2.03",
#                 branch_id = 0,
#                 account_type = 0,
#                 account_no = "100201003789",
#                 trade_account_no = "100201003789",
#                 password = "171025",
#                 tx_password = "",
#                 client_account = "100201003789",
#                 broker_account = "100201003789"
#                 )
#
#
# TDX_CFGS_TRADE = dict(
#                 qsid = 36,
#                 host = "58.57.121.98",
#                 port = 7700,
#                 version = "2.13",
#                 branch_id = 0,
#                 account_type = 0,
#                 account_no = "100201003789",
#                 trade_account_no = "100201003789",
#                 password = "171025",
#                 tx_password = "",
#                 client_account = "100201003789",
#                 broker_account = "100201003789"
#                 )
#
# # 中泰极速通
# TDX_CFGS_TRADE_XTP = dict(
#                 qsid = 36,
#                 host = "222.173.22.75",
#                 port = 7888,
#                 version = "6.11",
#                 branch_id = 0,
#                 account_type = 8,
#                 account_no = "100201003789",
#                 trade_account_no = "100201003789",
#                 password = "171025",
#                 tx_password = "",
#                 client_account = "100201003789",
#                 broker_account = "100201003789"
#                 )

Market_SH = 1
Market_SZ = 0
Market_NULL = 99
def getMaketTypeByCode(code):
    if not code:
        return Market_NULL
    if code[0] in ('0','3'):
        return Market_SZ
    return Market_SH


class TDX_StockMarket(stbase.Market):
    """行情接口"""
    def __init__(self):
        # self.ctx = {}

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
        self.thread_quotes = threading.Thread(target=self.quotesThread)

    def init(self,*args, **kwargs ):
        """
        host :  行情服务器地址
        port :  行情服务器端口


        :return:
        """
        self.logger = stbase.controller.getLogger()
        self.cfgs.update(kwargs)
        stbase.Market.init(self)
        return self

    def open(self):

        if not self.connectQuoteServer():
            return False

        stbase.Market.open(self)
        self.thread_quotes.start()
        return True

    def connectQuoteServer(self):
        self.hq_conn = None
        try:
            host = self.cfgs.get('quote_host')
            port = self.cfgs.get('quote_port')
            self.logger.info('Connect To HQ server..')
            self.hq_conn = TradeX2.TdxHq_Connect(host, port)
        except TradeX2.TdxHq_error, e:
            self.logger.error( e.message.decode('gbk').encode('utf8') )
        self.logger.info('HQ Server Connected.')
        return self.hq_conn


    def close(self):
        stbase.Market.close(self)
        self.thread_quotes.join()

    def quotesThread(self):
        """行情查询 线程"""
        freqs = self.cfgs.get('query_freq')
        while self.actived:
            time.sleep(freqs)
            try:
                if not self.hq_conn:
                    self.connectQuoteServer()
                self.quoteBar()
                self.quoteTick()
            except:
                self.hq_conn = None
                self.logger.error( traceback.print_exc() )


    def quoteTick(self):
        """分时数据"""

        qs = []
        if not self.tick_codes:
            return
        for code in self.tick_codes.keys():
            qs.append( (getMaketTypeByCode(code),code) )

        #查询行情记录
        errinfo, count, result = self.hq_conn.GetSecurityQuotes(qs)
        if errinfo != "":
            print errinfo.decode('gbk')
            self.hq_conn = None
        else:
            # print count
            lines = result.decode('gbk').split("\n")
            # print lines[0]
            for line in lines[1:]:
                # print line
                self.on_tick(line.split())

    def quoteBar(self):
        """查询k线"""
        cycle_cat_map = {
            '1m': 8,
            '5m': 0,
            '15m': 1,
            '30m': 2,
            '60m': 3,
            'd': 4,
            'w': 5,
            'm': 6,
            'q': 10,
            'y': 11
        }

        for k,codes in self.bar_codes.items():
            for code in codes:

                cat = cycle_cat_map[k]
                market = getMaketTypeByCode(code)
                # 获取最新的一根k线
                errinfo, count, result = self.hq_conn.GetSecurityBars(cat,market,code,0,2)
                if errinfo != "":
                    print errinfo.decode('gbk')
                    self.hq_conn = None
                else:
                    # print result.decode('gbk')
                    lines = result.decode('gbk').split("\n")
                    # print lines[0]
                    for line in lines[1:2]: # 不包含当前分钟动态变化的k线
                        # print line
                        self.on_bar(code,k,line.split('\t'))

    def initTradeObject(self,stock):
        """

        :param stock:  stbase.TradeObject
        :return:
        """
        # 初始化股票的初始参数， 交易限价、手续费等等
        if stock.inited:
            return

        # stk = self.ctx.Market.Stk(stock.code)
        #
        # stock.max_price = stk.MaxOrderPrice
        # stock.min_price = stk.MinOrderPrice
        # stock.stk = stk
        stock.inited = True
        return stock

    def getHistoryBars(self,code,cycle='1m',limit=100,inc_last=False):
        """获取历史k线
        剔除最后一根活动k线(盘中不能使用最后一根k线，或许是未完成计算的中间结果)
        result 以时间升序排列
        """

        result = [] # stbase.BarData()
        stock= self.product.getOrNewTradeObject(code)

        cycle_cat_map = {
            '1m': 8,'5m': 0,'15m': 1,
            '30m': 2,'60m': 3,'d': 4,
            'w': 5,'m': 6,'q': 10,
            'y': 11
        }

        cat = cycle_cat_map[cycle]
        market = getMaketTypeByCode(code)

        errinfo, count, text = self.hq_conn.GetSecurityBars(cat, market, code, 0, limit+1)
        if errinfo != "":
            print errinfo.decode('gbk')
            self.hq_conn = None
        else:
            lines = text.decode('gbk').split("\n")
            # print lines[0]
            for line in lines[1:-1]:  # 不包含当前分钟动态变化的k线
                data = self.barWrapped(code, cycle, line.split('\t'))
                result.append(data)

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
        # stock.stk.OnTick += partial(self.on_tick, stock)
        self.tick_codes[code]= {'last':None}
        return stock

    def subBar(self,code,handler,cycle='1m'):
        """订阅不同周期的k线事件"""

        stock = stbase.Market.subBar(self, code, handler, cycle)
        self.bar_codes[cycle].append(code)
        name ='{}-{}'.format(code,cycle)
        self.bar_last_data[name] = {'last':None}
        return stock

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


class TDX_StockTrader(stbase.Trader):
    """股票交易接口"""
    def __init__(self):
        stbase.Trader.__init__(self)
        self.trade_conn = None  # 交易通道
        self.logger = None
        self.cfgs = {'query_freq': .5}
        # self.cfgs.update(TDX_CFGS_TRADE)
        self.thread_query = threading.Thread(target=self.queryThread)
        self.actived = False
        self.position_list = {}  # 持仓记录
        self.gddm_list = {}     # 股东代码列表
        self.orders = {}       # 委托中的订单

    def init(self,*args,**kwargs):
        self.logger = stbase.controller.getLogger()
        self.cfgs.update(kwargs)
        stbase.Trader.init(self,**kwargs)
        return self

    def open(self):
        # 开始行情接收
        # if not self.connectServer():
        #     return False
        #
        self.connectServer()

        stbase.Trader.open(self)
        self.thread_query.start()
        return True

    def close(self):
        self.actived = False
        self.thread_query.join()

    def wait_for_shutdown(self,inf = 1000*1000):
        time.sleep(inf)

    def connectServer(self):
        self.trade_conn = None
        try:
            host = self.cfgs.get('host')
            port = self.cfgs.get('port')

            qsid = self.cfgs.get('qsid')
            version = self.cfgs.get('version')
            branch_id = self.cfgs.get('branch_id')
            account_type = self.cfgs.get('account_type')
            account_no = self.cfgs.get('account_no')
            trade_account_no = self.cfgs.get('trade_account_no')
            password = self.cfgs.get('password')
            tx_password = self.cfgs.get('tx_password')
            client_account = self.cfgs.get('client_account')
            broker_account = self.cfgs.get('broker_account')

            self.logger.info('Connect To HQ server..')
            TradeX2.OpenTdx(14, "6.40", 12, 0)
            self.trade_conn = TradeX2.Logon(qsid, host, port, version, branch_id, account_type, client_account, broker_account,
                                            password, tx_password)
        except TradeX2.error, e:
            print e.message.decode('gbk')
            self.logger.error(e.message.decode('gbk').encode('utf8'))
            return None
        self.logger.info('HQ Server Connected.')
        return self.trade_conn

    def queryThread(self):
        """查询持仓、资金、委托"""
        self.actived = True
        freqs = self.cfgs.get('query_freq')
        while self.actived:
            time.sleep(freqs)
            try:
                if not self.trade_conn:
                    self.connectServer()
                self.queryDatas()
            except:
                self.trade_conn = None
                self.logger.error(traceback.print_exc())


    def queryDatas(self):
        """
        查询各类持仓、订单、委托等信息
        :return:
        """
        # 0 资金
        # 1 股份
        # 2 当日委托
        # 3 当日成交
        # 4 可撤单
        # 5 股东代码
        # 6 融资余额
        # 7 融券余额
        # 8 可融证券
        categories = ( 0, 1,2,3,4,5)
        categories = ( 0,1,2,3,4,5 )
        categories = ( 0,1,4,5)
        # categories = ( 5,)
        functions = {
            0 : self.query_resp_funds,
            1 : self.query_resp_postions,
            # 2 : self.query_resp_today_orders,
            4 : self.query_resp_cancelable_orders,
            5: self.query_resp_gddm
        }
        # status, content  = self.trade_conn.QueryDatas(categories)
        # if status < 0:
        #     print content.decode('gbk')
        #     self.trade_conn = None  # 要求重连
        # else:
        #     for elem in content:
        for n in categories:
            if n == 5 and self.gddm_list:  # 股东代码已经查询就无需再查了
                continue
            errinfo, result = self.trade_conn.QueryData(n)
            if errinfo :
                print errinfo.decode('gbk')
                # self.trade_conn = None  # 要求重连
            else:
                # print n
                # print result.decode('gbk')
                lines = result.decode('gbk').split("\n")
                functions[n](lines[1:])


    def get_field_value(self,value,def_=0):
        value = value.strip()
        ret = def_
        # print 'get_value:' , value
        if value:
            ret = float(value)
        return ret

    def query_resp_today_orders(self,lines):
        """查询当日委托"""
        lines = map(lambda _: _.strip(), lines)
        lines = filter(lambda _: _, lines)
        self.orders = {}
        for line in lines:
            fs = line.split('\t')
            # print len(fs)
            order = stbase.OrderRecord()
            order.code = fs[11]
            order.name = fs[0]

            order.gddm = fs[12]
            order.direction = stbase.Constants.Buy
            if fs[1] == u'卖':
                order.direction = stbase.Constants.Sell

            order.order_id = fs[9]
            order.trans_id = ''
            order.order_price = self.get_field_value(fs[3])
            order.order_qty = int(self.get_field_value(fs[4]))
            order.qty_filled = int(self.get_field_value(fs[6]))
            order.qty_withdraw = 0  # int(self.get_field_value(fs[11]))
            self.orders[order.order_id] = order

        """
        - 东方证券 - 
        证券名称0	买卖标志1	买卖标志2	委托价格3	委托数量4	成交均价5	成交数量6	状态说明7	委托时间8	委托编号9	申报序号10	证券代码11	股东代码12	帐号类别13	备注	可撤单标志	交易所代码	撤单数量	委托属性	委托状态	保留信息
        恺英网络	    买	        0	        4.550	    400	        4.550	    400	        已成交	    09:30:55	167	        H700000032	002517	    0261758179	0           		 0	      2	0		已成交	
        恺英网络	卖	1	4.680	400	4.680	400	已成交	09:47:40	170	H700000108	002517	0261758179	0		0	2	0		已成交	
        恺英网络	卖	1	5.000	200	0.000	0	场内撤单	09:58:58	172	H700000151	002517	0261758179	0		0	2	200		场内撤单	
        辰欣药业	卖	1	18.170	200	18.170	200	已成交	10:03:01	174	0600000314	603367	A451079901	1		0	1	0		已成交	
        恺英网络	买	0	4.480	200	0.000	0	未成交	14:31:17	178	H700000431	002517	0261758179	0		1	2	0		已报	
        恺英网络	卖	1	4.830	200	0.000	0	未成交	14:48:03	182	H700000473	002517	0261758179	0		1	2	0		已报	

        """

    def query_resp_cancelable_orders(self,lines):
        """查询可撤销的委托"""
        lines = map(lambda _: _.strip(), lines)
        lines = filter(lambda _: _, lines)
        self.orders = {}
        for line in lines:
            fs = line.split('\t')
            # print len(fs)
            # for i, _ in enumerate(fs):
            #     print i, _.encode('utf-8')

            if self.cfgs.get('broker_name') == 'AIJIAN':
                order = stbase.OrderRecord()
                order.code = fs[1]
                order.name = fs[2]

                order.gddm = fs[13]
                order.direction = stbase.Constants.Buy
                if fs[4] == u'卖出':
                    order.direction = stbase.Constants.Sell

                order.order_id = fs[8]
                order.trans_id = ''
                order.order_price = self.get_field_value(fs[6])
                order.order_qty = int(self.get_field_value(fs[7]))
                order.qty_filled = int(self.get_field_value(fs[10]))
                order.qty_withdraw = int(self.get_field_value(fs[11]))
                self.orders[order.order_id] = order
                # print order.dict()
                """
                0 09:52:30
                1 002517
                2 恺英网络
                3 0
                4 买入
                5 已报
                6 3.7000
                7 200
                8 51
                9 0.0000
                10 0
                11 0
                12 买卖
                13 0237617162
                14 委托
                15 0
                16 0
                17 
                18 08D92910
                """
            if self.cfgs.get('broker_name') == 'DONGFANG':
                order = stbase.OrderRecord()
                order.code = fs[11]
                order.name = fs[0]

                order.gddm = fs[12]
                order.direction = stbase.Constants.Buy
                if fs[1] == u'卖':
                    order.direction = stbase.Constants.Sell

                order.order_id = fs[9]
                order.trans_id = ''
                order.order_price = self.get_field_value(fs[3])
                order.order_qty = int(self.get_field_value(fs[4]))
                order.qty_filled = int(self.get_field_value(fs[6]))
                order.qty_withdraw = 0 #int(self.get_field_value(fs[11]))
                self.orders[order.order_id] = order
                # print order.dict()
        # print 'query order cancellable end.'
        """
        ** 注意 ： 不同的证券通道返回的格式均不同 
        - 东方证券 - 
        证券名称0	买卖标志1	买卖标志2	委托价格3	委托数量4	成交价格5	成交数量6	状态说明7	委托时间8	委托编号9	申报序号10	证券代码11	股东代码12	帐号类别13	备注	交易所代码	委托状态	保留信息
        恺英网络	卖	1	5.000	200	0.000	0	未成交	09:58:58	172	H700000151	002517	0261758179	0		2	已报	
        """

        """
        委托日期0	委托时间1	证券代码2	证券名称3	状态说明4	买卖标志5	
        买卖标志6	委托价格7 委托数量8	委托编号9	成交数量10	撤单数量11	股东代码12	帐号类别13	
        	资金帐号14	备注	句柄	保留信息
        """


    def query_resp_gddm(self,lines):
        """股东代码查询返回"""
        lines = map(lambda _: _.strip(), lines)
        lines = filter(lambda _: _, lines)
        self.gddm_list = {}
        for line in lines:
            fs = line.split('\t')
            # print len(fs)
            name = fs[0]
            type_ = int(fs[2])

            # for i, _ in enumerate(fs):
            #     print i, _.encode('utf-8')

            self.gddm_list[type_] = fs[0]


            # _ = self.gddm_list.get(type_)
            # if not _:
            #     self.gddm_list[type_] = []
            #     _ = self.gddm_list.get(type_)
            #
            # type_.append( fs[0])
        # print self.gddm_list
        """
        - 东方证券 - 
        股东代码0	股东名称1	帐号类别2	资金帐号3	指定交易4	保留信息
        A451079901	XXX	1	    06034051	0	
        0261758179	XXX	0	    06034051	0	
        
        - 中泰证券 - 
        股东代码0	股东名称1	帐号类别2	资金帐号3	融资融券标识4	指定交易5	句柄	保留信息
        0252085695	孙鹏	0	0	0	0	0741E2D0	主股东
        A338780150	孙鹏	1	0	0	1	0741E2D0	主股东
        0571803172	孙鹏	0	0	0	0	0741E2D0	
        F138928144	孙鹏	1	0	0	1	0741E2D0
        """

    def query_resp_postions(self,lines):
        """持仓返回"""
        lines = map(lambda _: _.strip(), lines)
        lines = filter(lambda _: _, lines)
        self.position_list = {}
        for line in lines:
            fs = line.split('\t')
            # print len(fs)
            # for i,_ in enumerate(fs):
            #     print i , _.encode('utf-8')

            if self.cfgs.get('broker_name') == 'AIJIAN':
                pos = TdxPosition()
                pos.code = fs[0]
                pos.name = fs[1]
                pos.qty_current = self.get_field_value(fs[2])
                pos.qty_pos = pos.qty_current
                # pos.qty_td = pos.qty_current
                pos.qty_yd = self.get_field_value(fs[3])
                pos.qty_td = pos.qty_current - pos.qty_yd
                pos.last_price = self.get_field_value(fs[7])
                pos.gddm = fs[10]
                self.position_list[pos.code] = pos
                # print pos.dict()
                """
                0 002517
                1 恺英网络
                2 700
                3 200
                4 -62.940
                5 3.999
                6 -1.98
                7 3.920
                8 2744.000
                9 深圳A股
                10 0237617162
                11 0
                12 0
                13 16711680
                14 
                15 08D4DA28
                """

            if self.cfgs.get('broker_name') == 'DONGFANG':
                pos = TdxPosition()
                pos.code = fs[0]
                pos.name = fs[1]
                pos.qty_current = self.get_field_value(fs[2])
                pos.qty_yd = self.get_field_value(fs[4])
                pos.last_price = self.get_field_value(fs[8])
                pos.gddm = fs[12]
                self.position_list[pos.code] = pos
                # print pos.dict()

        """ 
        - 爱建证券 - 
        证券名称	证券数量	可卖数量	成本价	浮动盈亏	盈亏比例(%)	最新市值	当前价	今买数量	今卖数量	证券代码	股东代码	帐号类别	交易所代码	备注	保留信息
        恺英网络	4200	2900	4.219	-1255.000	-7.09	16464.000	3.920			002517	0261758179	0	0	开仓证券	
        
  
        - 东方证券 - 
        证券名称	证券数量	可卖数量	成本价	浮动盈亏	盈亏比例(%)	最新市值	当前价	今买数量	今卖数量	证券代码	股东代码	帐号类别	交易所代码	备注	保留信息
        辰欣药业	0	0	0.000	-50.780	0.00	0.000	18.420			603367	A451079901	1	1	开仓证券	
        恺英网络	600	0	7.016	-1305.460	-31.01	2904.000	4.840			002517	0261758179	0	0	开仓证券	

        - 中泰证券 - 
        
        18
        证券代码0	证券名称1	证券数量2	库存数量3	可卖数量4	余券数量5	参考成本价6	盈亏成本价7	当前价8	参考市值9	参考盈亏10	参考盈亏比例(%)11	股东代码12	帐号类别13	交易所代码14	资金帐号15	交易所名称16	句柄	保留信息
600010	包钢股份	100	100	100		1.840	1.840	1.790	179.000	-5.000	-2.72	A338780150	1	1	100201003789	上海A股	073F5720	

        """
    def query_resp_funds(self, lines):
        """资金返回"""
        lines = map(lambda _:_.strip(),lines)
        lines = filter(lambda _:_,lines)
        for line in lines:
            fs = line.strip().split('\t')
            # print len(fs)
            # for i, _ in enumerate(fs):
            #     print i, _.encode('utf-8')

            if self.cfgs.get('broker_name') == 'AIJIAN':
                if fs[0] == '0': # 人民币
                    self.stat.balance = self.get_field_value(fs[1])
                    self.stat.usable_amount = self.get_field_value(fs[2])
                    self.stat.frozen_amount = 0 # self.get_field_value(fs[4])
                    self.stat.drawable_amount = self.get_field_value(fs[4])
                    self.stat.reference_value =  self.get_field_value(fs[6])
                    self.stat.asset_amount = self.get_field_value(fs[5])
                """
                0 0
                1 39027.39
                2 37057.29
                3 0.00
                4 37057.29
                5 39801.29
                6 2744.00
                7 
                8 08C3ECD8
                """
            if self.cfgs.get('broker_name') == 'DONGFANG':
                if fs[0] == '0': # 人民币
                    self.stat.balance = self.get_field_value(fs[1])
                    self.stat.usable_amount = self.get_field_value(fs[2])
                    self.stat.frozen_amount = self.get_field_value(fs[3])
                    self.stat.drawable_amount = self.get_field_value(fs[5])
                    self.stat.reference_value = 0 # self.get_field_value(fs[6])
                    self.stat.asset_amount = self.get_field_value(fs[4])

                    # self.stat.frozen_buy = self.get_field_value(fs[8])
                    # self.stat.frozen_sell = self.get_field_value(fs[9])


        """
        - 东方证券 - 
        币种0	资金余额1	可用资金2	冻结资金3	总资产4	    可取资金5	融资金额6	模式7	最新市值8	融资负债	融券负债	保留信息
        0	    7034.290	9798.720	901.000	    13591.720	7034.290		0	            2892.000	0.000	0.000	
        1	0.000	0.000	0.000	0.000	0.000		0	0.000	0.000	0.000	
        2	0.000	0.000	0.000	0.000	0.000		0	0.000	0.000	0.000	

        - 中泰证券 - 
        资金帐号0	        币种1	    资金余额2	    可用资金3	    冻结资金4	可取资金5	参考市值6	总资产7	买入冻结资金8	 卖出冻结资金9	取柜台可买数量10	账户信用值11	可用信用额度12	句柄	保留信息
        100201003789	0	    750.71	    0.00		0.00	750.71	750.71	0.00	0			0741DFC0
        """

    def onRtsChanged(self,rts_list):
        """委托或成交回报"""
        fmt = '%Y-%m-%d %H:%M:%S'
        tr_list = []
        for _ in rts_list:

            tr = stbase.TradeReturn()
            tr.type = _.Type
            tr.order_id = _.OrigSerialNo
            tr.user_id = _.OrigSource
            tr.protfolio_num = _.PortfolioNum
            tr.code = _.ServerCode
            tr.direction = stbase.Constants.Buy
            if _.BSType == 'S':
                tr.direction = stbase.Constants.Sell

            tr.oc = stbase.Constants.Open
            if _.OCFlag == 'C':
                tr.oc = stbase.Constants.Cover
            tr.order_price = _.OrderPrice
            tr.order_qty = _.OrderQty


            # print _.OrderTime,type(_.OrderTime)
            if _.OrderTime:
                tr.order_time = datetime.datetime.fromtimestamp(_.OrderTime)
            if _.KnockTime:
                tr.knock_time = datetime.datetime.fromtimestamp(_.KnockTime)
            tr.knock_code = _.KnockCode
            tr.knock_price = _.KnockPrice
            tr.knock_qty = _.KnockQty
            tr.knock_amount = _.KnockAmt
            tr.total_withdraw_qty = _.TotalWithdrawQty
            tr.total_knock_qty = _.TotalKnockQty
            tr.total_knock_amount = _.TotalKnockAmt
            tr.status = stbase.Constants.OrderStatus.Unknown

            if _.StatusCode == 'Registered':
                tr.status = stbase.Constants.OrderStatus.Registered
            elif _.StatusCode == 'Pending_Dealing':
                tr.status = stbase.Constants.OrderStatus.Pending_Dealing
            elif _.StatusCode == 'Rejected':
                tr.status = stbase.Constants.OrderStatus.Rejected
            elif _.StatusCode == 'Pending_Cancel':
                tr.status = stbase.Constants.OrderStatus.Pending_Cancel
            elif _.StatusCode == 'Cancelled':
                tr.status = stbase.Constants.OrderStatus.Cancelled
            elif _.StatusCode == 'Partially_Pending_Cancel':
                tr.status = stbase.Constants.OrderStatus.Partial_Pending_Cancel
            elif _.StatusCode == 'Partially_Cancelled':
                tr.status = stbase.Constants.OrderStatus.Partial_Cancelled
            elif _.StatusCode == 'Partially_Filled':
                tr.status = stbase.Constants.OrderStatus.Partial_Filled
            elif _.StatusCode == 'Fully_Filled':
                tr.status = stbase.Constants.OrderStatus.Fully_Filled
            elif _.StatusCode == 'Auditing':
                tr.status = stbase.Constants.OrderStatus.Auditing
            elif _.StatusCode == 'AuditError':
                tr.status = stbase.Constants.OrderStatus.AuditError

            tr_list.append(tr)

        stbase.Trader.onRtsChanged(self, tr_list)
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
        Buy = 0
        Sell = 1
        direction = Buy
        if order_req.direction == stbase.Constants.Sell:
            direction = Sell
        # print order_req.dict()
        """
        委托报价方式
        0 限价委托; 上海限价委托 / 深圳限价委托
        1 市价委托(深圳对方最优价格)
        2 市价委托(深圳本方最优价格)
        3 市价委托(深圳即时成交剩余撤销)
        4 市价委托(上海五档即成剩撤 / 深圳五档即成剩撤) 5 市价委托(深圳全额成交或撤销)
        6 市价委托(上海五档即成转限价)
        """
        order_type = 0
        gddm = self.get_gddm(order_req.code)   # 股东代码

        status,content = self.trade_conn.SendOrder(direction,order_type,gddm,order_req.code,order_req.price,order_req.quantity)
        if status < 0:
            print "error: " + content.decode('gbk')
        else:
            print content.decode('gbk')
        order_id = ''
        return order_id

    def get_code_by_order_id(self,order_id):
        """查询委托单的证券代码"""
        order = self.orders.get(order_id)
        if order:
            return order.code
        else:
            print self.orders
        return ''

    def get_market_by_order_id(self,order_id):
        """根据订单编号查询市场编号"""
        code = self.get_code_by_order_id(order_id)

        return getMaketTypeByCode(code)

    def cancelOrder(self,order_id):
        market_id = self.get_market_by_order_id(order_id)
        if market_id == Market_NULL:
            print 'error: MarketID is Null :',order_id
            return
        errinfo,result = self.trade_conn.CancelOrder(market_id,order_id)
        if errinfo:
            print errinfo.decode('gbk')
        else:
            print result.decode('gbk')


    def getPosition(self,code='',strategy_id='',direction= stbase.Constants.Buy):
        """查询指定 股票代码或者指定策略的持仓记录"""
        if code:
            pos = self.position_list.get(code)
            if not pos:
                pos = stbase.Position()
            return pos
        return self.position_list.values()

    def getOrders(self,order_id='',code='',strategy_id=''):
        """查询委托信息，状态包括： 未成、部分成、全成、错误
            strategy_id 作为 委托的 orign source  字段
        """

        return self.orders.values()


    def getAmountUsable(self):
        """账户可用资金"""
        return self.stat.usable_amount

    def getAmountAsset(self):
        """现货总资产"""
        return self.stat.asset_amount

class TdxPosition(stbase.Position):
    """持仓记录"""
    def __init__(self):
        stbase.Position.__init__(self)
        self.name = ''      # 证券名称
        self.last_price = 0  # 当前价格
        self.gddm = ''      # 股东代码

if __name__ == '__main__':
    trader = TDX_StockTrader().init()
    trader.open()
    trader.wait_for_shutdown()
