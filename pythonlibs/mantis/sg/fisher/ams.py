#coding:utf-8

"""
1. ASM BUGS

  ams软件中， 手动终止 close() 不能调用 Strategy.Exit() , 否则会卡死
  订阅tick/bar 时， code 不支持unicode

"""
import time,datetime
from collections import OrderedDict
from functools import partial
from utils.importutils import import_module,import_class
from utils.useful import singleton
from utils.timeutils import timestamp_to_str
import stbase


class ASM_StockMarket(stbase.Market):
    """兴业证券AMS行情接口"""
    def __init__(self):
        self.ctx = None
        stbase.Market.__init__(self,None)

    def init(self,ctx):
        self.ctx = ctx
        stbase.Market.init(self)
        return self


    def initTradeObject(self,stock):
        """

        :param stock:  stbase.TradeObject
        :return:
        """
        # 初始化股票的初始参数， 交易限价、手续费等等
        if stock.inited:
            return
        stock.code = str(stock.code)
        stk = self.ctx.Market.Stk(stock.code)

        stock.max_price = stk.MaxOrderPrice
        stock.min_price = stk.MinOrderPrice
        stock.stk = stk
        stock.inited = True
        return stock

    def getHistoryBars(self,code,cycle='1m',limit=100,inc_last=False,lasttime=None):
        """获取历史k线
        剔除最后一根活动k线(盘中不能使用最后一根k线，或许是未完成计算的中间结果)
        result 以时间升序排列
        """
        # if self.bar_nums.get(ktype,0) == 0:
        #     return ()

        stock= self.product.getOrNewTradeObject(code)
        stk = stock.stk
        bars = {'1m':stk.MinuteData1,
                '5m':stk.MinuteData5,
                '15m':stk.MinuteData15,
                '30m':stk.MinuteData30,
                'd':stk.DailyData,
                'w':stk.WeeklyData,
                'm':stk.MonthlyData,
                'q':stk.QuarterlyData,
                'y':stk.YearlyData
        }
        result = []
        kdata = bars.get(cycle)
        max = kdata.Count
        offset = 0
        if not inc_last:
            offset = -1
        # print max - limit + offset, max + offset
        for num in range(max - limit + offset, max + offset):  # 不包含最后一根
            d = kdata[num]
            bar = stbase.BarData()
            bar.close = d.Close
            result.append(bar)
            # result.append(d.Close)
            # print d.Close
        return result

    def getYdClosePrice(self,code):
        """查詢昨日 收盤價
         ? 如果盤后查詢，則取最後一根而不是倒數第二

        """
        import stutils
        if not stutils.Stocks.in_trading_time():
            stbase.println(" not in trading time ..")
            return self.getHistoryBars(code,'d', 2,True)[-1].Close
        return self.getHistoryBars(code,'d', 2)[-1].Close

    def subTick(self, code, handler):
        """订阅分时行情"""
        code = str(code)
        stock = stbase.Market.subTick(self, code, handler)
        stock.stk.OnTick += partial(self.on_tick, stock)
        # print 'subTick:' ,code,handler
        return stock

    def subBar(self,code,handler,cycle='1m'):
        """订阅不同周期的k线事件"""
        code = str(code)
        stock = stbase.Market.subBar(self,code, handler, cycle)
        stk = self.ctx.Market.Stk(stock.code)
        handlers = {
            '1m': (stk.MinuteData1.OnNewBar,self.on_bar_m1),
            '5m': (stk.MinuteData5.OnNewBar,self.on_bar_m5),
            '15m': (stk.MinuteData15.OnNewBar,self.on_bar_m15),
            '30m': (stk.MinuteData30.OnNewBar,self.on_bar_m30),
            '60m': (stk.MinuteData60.OnNewBar,self.on_bar_m60),
            'd': (stk.DailyData.OnNewBar,self.on_bar_daily),
            'w': (stk.WeeklyData.OnNewBar,self.on_bar_week),
            'm': (stk.MonthlyData.OnNewBar,self.on_bar_month),
            'q': (stk.QuarterlyData.OnNewBar,self.on_bar_quarter),
            'y': (stk.YearlyData.OnNewBar,self.on_bar_year)
        }

        a,b = handlers.get(cycle)
        a += partial(b,stock)
        return stock


    def on_tick(self, stock,stk):
        """行情进入，生成 TickData()对象，推送到 stbase.Market的处理工作队列"""
        data = stbase.TickData()
        data.code = stock.code
        data.trade_object = stock
        data.sys_time = datetime.datetime.now()

        price = data.price
        # print 'on_tick..'
        fmt = '%Y-%m-%d %H:%M:%S'
        # print stk.KnockTime
        # price.time = datetime.datetime.strptime(fmt,stk.KnockTime)
        # price.time = time.strftime(fmt, stk.KnockTime)
        price.time = datetime.datetime(stk.KnockTime.tm_year,
                                       stk.KnockTime.tm_mon,
                                       stk.KnockTime.tm_mday,
                                       stk.KnockTime.tm_hour,
                                       stk.KnockTime.tm_min,
                                       stk.KnockTime.tm_sec)
        price.last = stk.KnockPrice
        price.yd_close = stk.ClosePrice
        price.qty = stk.KnockQty
        price.amount =  stk.KnockAmt
        price.total_qty = stk.TotalKnockQty
        price.total_amount = stk.TotalKnockAmt
        price.diff = stk.Diff
        price.diff_rate = stk.DiffRate
        price.sell_1 =  stk.SellPrice1
        price.sell_2 =  stk.SellPrice2
        price.sell_3 = stk.SellPrice3
        price.sell_4 = stk.SellPrice4
        price.sell_5 = stk.SellPrice5
        price.sell_qty_1 = stk.SellQty1
        price.sell_qty_2 = stk.SellQty2
        price.sell_qty_3 = stk.SellQty3
        price.sell_qty_4 = stk.SellQty4
        price.sell_qty_5 = stk.SellQty5

        price.buy_1 = stk.BuyPrice1
        price.buy_2 = stk.BuyPrice2
        price.buy_3 = stk.BuyPrice3
        price.buy_4 = stk.BuyPrice4
        price.buy_5 = stk.BuyPrice5

        price.buy_qty_1 = stk.BuyQty1
        price.buy_qty_2 = stk.BuyQty2
        price.buy_qty_3 = stk.BuyQty3
        price.buy_qty_4 = stk.BuyQty4
        price.buy_qty_5 = stk.BuyQty5

        data.trade_object.price = data.price

        self.putData(data)          # 置入处理队列等待线程读取


    def on_bar_triggered(self,stock,cycle,kdata,num):
        """k线数据触发"""
        bar = kdata[num]
        data = stbase.BarData()
        data.amount = bar.Amount
        data.open = bar.Open
        data.high = bar.High
        data.low = bar.Low
        data.close = bar.Close
        data.vol = bar.Vol

        year,mon,day,hour,min,sec = bar.DateTime[:4],\
                                    bar.DateTime[4:6],\
                                    bar.DateTime[6:8],\
                                    bar.DateTime[8:10],\
                                    bar.DateTime[10:12],\
                                    bar.DateTime[12:14]

        data.time = datetime.datetime(int(year),int(mon),int(day),int(hour),int(min),int(sec))

        data.sys_time = datetime.datetime.now()
        data.code = stock.code
        data.trade_object = stock

        data.cycle = cycle
        data.num = num      # bar的最大流水
        self.putData(data)

    def on_bar_m1(self,stock,bar,num):
        self.on_bar_triggered(stock,'1m',bar,num)

    def on_bar_m5(self,stock,bar,num):
        self.on_bar_triggered(stock,'5m',bar,num)

    def on_bar_m15(self,stock,bar,num):
        self.on_bar_triggered(stock,'15m', bar, num)

    def on_bar_m30(self,stock,bar,num):
        self.on_bar_triggered(stock,'30m', bar, num)

    def on_bar_m60(self,stock,bar,num):
        self.on_bar_triggered(stock,'60m', bar, num)

    def on_bar_daily(self,stock,bar,num):
        self.on_bar_triggered(stock,'d', bar, num)

    def on_bar_week(self,stock,bar,num):
        self.on_bar_triggered(stock,'w', bar, num)

    def on_bar_month(self,stock,bar,num):
        self.on_bar_triggered(stock,'m', bar, num)

    def on_bar_quarter(self,stock,bar,num):
        self.on_bar_triggered(stock,'q', bar, num)

    def on_bar_year(self,stock,bar,num):
        self.on_bar_triggered(stock,'y', bar, num)

    def close(self):
        # self.ctx.Strategy.Exit()
        stbase.Market.close(self)
        print 'Market closed..'

class ASM_StockTrader(stbase.Trader):
    """兴业AMS股票交易对象"""
    def __init__(self):
        stbase.Trader.__init__(self)
        self.ctx = None

    def init(self,ctx):
        self.ctx = ctx

        self.ctx.Strategy.Product.Changed += self.onPositionChanged
        self.ctx.Strategy.RtsChanged += self.onRtsChanged
        return self

    def open(self):
        # 开始行情接收
        pass

    def close(self):
        pass


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

        stbase.Trader.onRtsChanged(self,tr_list)
        # stbase.println('onRtsChanged(), size:%s'%(len(rts_list)))

    def onPositionChanged(self):
        # 持仓和资金变更通知
        stbase.Trader.onPositionChanged(self)
        # stbase.println('onPositionChanged() , ')

    def sendOrder(self,order_req = stbase.OrderRequest(code='')):
        """发送订单
            :param: order_req : stbase.OrderRequest
        """
        direction = 'B'
        if order_req.direction == stbase.Constants.Sell:
            direction = 'S'
        # print order_req.dict()
        orderitem = self.ctx.ResTable.OrderItem(order_req.code, direction,
                                            order_req.quantity, order_req.price)
        serialno = self.ctx.Strategy.Order(orderitem)
        res = stbase.OrderReturn()
        res.code = order_req.code
        res.request = order_req
        res.order_id = serialno

        order_req.order_id = serialno
        
        return serialno

    def cancelOrder(self,order_id):
        self.ctx.Strategy.WithDraw(order_id)

    def getPosition(self,code='',strategy_id='',direction= stbase.Constants.Buy):
        """查询指定 股票代码或者指定策略的持仓记录
            未提供code则查询返回当前所有持仓记录 [] ,
            否则返回单个持仓对象 stbase.Position()
        """
        result = []
        # pos_list = self.ctx.Strategy.Product.All_Pos
        pos_list = self.ctx.Strategy.Product.S_Pos
        for _ in pos_list:
            # print _.ServerCode
            pos = stbase.Position()
            pos.code = _.ServerCode
            pos.product = stbase.Product.STOCKS
            pos.qty_current = _.PositionQty    # 持仓余额(清算之后持仓)
            pos.qry_pos = _.PositionQty        # 实时持仓
            pos.qty_td = _.TdQty         # 今日持仓,可用数(可卖数)
            pos.qty_yd = _.YdQty         # 昨仓
            pos.qty_yd_frozen = _.TdClosingqty  # 昨冻结
            pos.qty_td_frozen = _.YdClosingqty  # 今冻结
            pos.margin_amount = _.MarginUsedAmt  # 保证金占用
            pos.open_avg_price = _.OpenAvgPrice # 开仓均价
            pos.cost_amount = _.PostCostAmt    # 成本金额

            if code :
                if _.ServerCode == code:
                    return pos
            else:
                result.append(pos)

        if code :
            return stbase.Position()

        return result


    def getOrders(self,order_id='',code='',strategy_id=''):
        """查询委托信息，状态包括： 未成、部分成、全成、错误
            strategy_id 作为 委托的 orign source  字段
        """
        result =[]
        source = 'C'
        # if strategy_id:
        #     source = strategy_id

        orders = self.ctx.Strategy.GetOrdersByOrigSource(source)
        for _ in orders:
            order = stbase.OrderRecord()
            order.user_id = _.OrigSource
            # order.order_time = _.OrderTime
            fmt = '%Y-%m-%d %H:%M:%S'
            order.order_time =  datetime.datetime.fromtimestamp(_.OrderTime)
            order.trans_id = _.PortfolioNum
            order.contract_id = _.ContractNum
            order.code = _.ServerCode
            order.name = _.StkName
            order.direction = stbase.Constants.Buy
            # print _.BSType
            if _.BSType == 'S':
                order.direction = stbase.Constants.Sell
            order.oc = stbase.Constants.Open
            if _.OCFlag == 'C':
                order.oc = stbase.Constants.Cover
            order.hedge = str(_.F_HedgeFlag)

            order.status = stbase.Constants.OrderStatus.Unknown
            if _.StatusCode == 'Registered':
                order.status = stbase.Constants.OrderStatus.Registered
            elif _.StatusCode == 'Pending_Dealing':
                order.status = stbase.Constants.OrderStatus.Pending_Dealing
            elif _.StatusCode == 'Rejected':
                order.status = stbase.Constants.OrderStatus.Rejected
            elif _.StatusCode == 'Pending_Cancel':
                order.status = stbase.Constants.OrderStatus.Pending_Cancel
            elif _.StatusCode == 'Cancelled':
                order.status = stbase.Constants.OrderStatus.Cancelled
            elif _.StatusCode == 'Partially_Pending_Cancel':
                order.status = stbase.Constants.OrderStatus.Partial_Pending_Cancel
            elif _.StatusCode == 'Partially_Cancelled':
                order.status = stbase.Constants.OrderStatus.Partial_Cancelled
            elif _.StatusCode == 'Partially_Filled':
                order.status = stbase.Constants.OrderStatus.Partial_Filled
            elif _.StatusCode == 'Fully_Filled':
                order.status = stbase.Constants.OrderStatus.Fully_Filled

            order.order_price = _.OrderPrice
            order.order_qty = _.OrderQty
            order.qty_filled = _.KnockQty
            order.qty_unfilled =  _.UnKnockQty
            order.qty_withdraw = _.WithdrawQty

            order.order_id = _.OrigSerialNo
            order.error.message = _.ErrMsg

            matched = True
            if order_id or code:
                matched = False

            if order_id and  order.order_id == order_id:
                matched = True
            if code and code == order.code:
                matched = True
            if matched:
                result.append(order)

        return  result

    def getAmountUsable(self):
        """账户可用资金"""
        prd = self.ctx.Strategy.Product
        return prd.Stk_UseableAmt

    def getAmountAsset(self):
        """现货总资产"""
        prd = self.ctx.Strategy.Product
        return prd.Stk_CurrentAmtForAsset

# ------------------------------------------
class ResTable:
    def __init__(self):
        OrderItem = None  # # AMS 全局资源对象


@singleton
class Context:
    def __init__(self):
        self.Market = None  # AMS 全局资源对象
        self.Strategy = None  # AMS 全局资源对象
        self.ResTable = ResTable()
        self.data = {}
        self.controller = stbase.controller

    def init(self, market, strategy,home_path='./'):
        self.Market = market
        self.Strategy = strategy
        self.Strategy.OnExiting += self.onExit
        return self

    def launch(self, module):
        """加载策略"""

        # module = import_module(name)
        module.context = self
        module.init(self)

    def onExit(self):
        import stbase
        stbase.println('onExit()..')
        stbase.controller.stop()
        stbase.println('-- Reached End. System Shutdown. -- ')



"""
usage:
===== 
from sg.xingye.context import Context

from sg.fisher.ams import Context
Context().init(Market,Strategy)
Context().ResTable.OrderItem = OrderItem
Context().launch('sg.fisher.strategy_ams_sample')

"""

# context = None
# stbase.controller.init('./')
# stbase.stocks.setup(ASM_StockMarket().init(context),ASM_StockTrader().init(context))
# stbase.stocks.market.setupRecorder(stbase.MarketFileRecorder())
# stbase.controller.addStrategy(ASM_Strategy())
# stbase.controller.run()


