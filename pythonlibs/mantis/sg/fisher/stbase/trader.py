#coding:utf-8

from base import *
from order import *
from controller import *

class Trader(object):
    """交易接口，依据不同的券商接口"""
    def __init__(self):
        # self.pos_list = OrderedDict()   # 总体持仓记录
        self.stat = AccountStat()       # 当前账户状态
        self.product = None
        self.strategies = []        # 策略列表

    def init(self, *args, **kwargs):
        return self

    def open(self):
        # 开始行情接收
        pass

    def close(self):
        pass

    def getPosition(self,code='',strategy_id=''):
        pass

    def getOrders(self,code=''):
        pass

    def getTradeRecords(self,order_id_):
        pass
    
    def sendOrder(self,order_req):
        """发送订单"""
        return OrderReturn()

    def cancelOrder(self,order_id):
        pass

    def waitOrder(self,order_id,timeout=1):
        """等待订单成交事件， 包含：拒绝、部分成、全成、超时 """
        pass

    def getAmountUsable(self):
        """现货可用资金"""
        return 0

    def getAmountAsset(self):
        """现货总资产"""
        return 0

    def onRtsChanged(self,rts_list):
        """委托或成交回报"""
        strategies = TradeController().strategies.values()
        for st in strategies:
            st.onRtsChanged(rts_list)

    def onPositionChanged(self):
        # 持仓和资金变更通知
        strategies = TradeController().strategies.values()
        for st in strategies:
            st.onPositionChanged()
