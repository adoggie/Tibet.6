#coding:utf-8

"""
回测模块:
行情交易模拟
1. 模拟行情生成 ，同时只能对一种行情规格模拟，tick or bar
2. 模拟持仓、订单、账户查询接口

"""

import datetime
import stbase


class BackStockMarket(stbase.Market):
    """
    模拟市场行情对象，调用行情生成器来获得tick和bar数据，
    同样行情生成器也提供历史行情的查询
    仅支持同时回测一只股票
    """
    def __init__(self):
        stbase.Market.__init__(self,None)
        self.last_tick = None
        self.last_bar = None  #  记录最近到达的行情记录


    def onBar(self,bar):
        self.last_bar = bar
        stbase.Market.onBar(self,bar)

    def onTick(self,tick):
        self.last_tick = tick
        stbase.Market.onTick(self,tick)

    def getHistoryBars(self,code,cycle,limit):
        end = None
        if self.last_bar:
            end = self.last_bar.time
        return self.generator.getHistoryBars(code,cycle,limit,end= end )

class BackStockTrader(stbase.Trader):
    """
    模拟交易对象
    """
    def __init__(self):
        stbase.Trader.__init__(self)

    def getPosition(self,code='',strategy_id=''):
        """模拟持仓查询，返回最大可用持仓量"""
        result = []

        pos = stbase.Position()
        pos.code = code
        pos.product = stbase.Product.STOCKS
        pos.qty_current = 99999999    # 持仓余额(清算之后持仓)
        pos.qry_pos = 999999        # 实时持仓
        pos.qty_td = 999999         # 今日持仓,可用数(可卖数)
        pos.qty_yd = 999999         # 昨仓
        pos.qty_yd_frozen = 0  # 昨冻结
        pos.qty_td_frozen = 0  # 今冻结
        pos.margin_amount = 0  # 保证金占用
        pos.open_avg_price = 0 # 开仓均价
        pos.cost_amount = 0    # 成本金额

        return pos

    def getOrders(self,order_id='',code='',strategy_id=''):
        """查询委托信息，状态包括： 未成、部分成、全成、错误
            strategy_id 作为 委托的 orign source  字段
        """
        result =[]

        if True:
            order = stbase.OrderRecord()
            order.user_id = ''
            fmt = '%Y-%m-%d %H:%M:%S'
            # order.order_time =  datetime.datetime.fromtimestamp(_.OrderTime)
            order.trans_id = 111
            order.contract_id = '232'
            order.code = code
            order.name = ''
            order.direction = stbase.Constants.Buy
            # # print _.BSType
            # if _.BSType == 'S':
            #     order.direction = stbase.Constants.Sell
            # order.oc = stbase.Constants.Open
            # if _.OCFlag == 'C':
            #     order.oc = stbase.Constants.Cover
            # order.hedge = str(_.F_HedgeFlag)

            order.status = stbase.Constants.OrderStatus.Fully_Filled

            # order.order_price = _.OrderPrice
            # order.order_qty = _.OrderQty
            # order.qty_filled = _.KnockQty
            # order.qty_unfilled =  _.UnKnockQty
            # order.qty_withdraw = _.WithdrawQty

            order.order_id = order_id
            # order.error.message = _.ErrMsg
            result.append(order )

        return  result

    def getAmountUsable(self):
        """账户可用资金"""
        return 999999999

    def getAmountAsset(self):
        """现货总资产"""
        return 999999999

    def sendOrder(self,order_req):
        """发送订单"""
        # res = stbase.Trader.sendOrder(self,order_req)
        # res.order_id = 9999
        order_id = 9999
        order_req.order_id = order_id
        return order_id