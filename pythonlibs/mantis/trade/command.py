# coding: utf-8

from vnpy.trader.vtObject import *
from mantis.fundamental.flask.webapi import CallReturn
# class Command(object):
#     def __init__(self,name):
#         self.name = name

class StartTradeAdapter(object):
    """请求TradeAdapter服务启动
        场景： 调度服务器或者runner请求launcher启动tradeAdapter服务进程
    """
    NAME = 'start_trade_adapter'
    def __init__(self):
        pass

class KeepAlive(object):
    """请求指定服务器保持运行，服务 A依赖B的运行，A定时发送此消息到B系统，B接收到保持自己服务器运行，否则B自行结束"""
    NAME = 'keepalive'
    def __init__(self):
        pass

class ServiceStatusBroadcast(object):
    """服务器定时广播自己的运行状态 pub-channel """
    NAME = 'service_status_broadcast'
    def __init__(self):
        self.service_id = ''    #
        self.service_type =  ''
        self.http = ''          # 服务器运行的web管理接口地址

class SendOrder(VtOrderReq):
    NAME = 'send_order'
    def __init__(self):
        VtOrderReq.__init__(self)

    class Result(object):
        def __init__(self):
            self.value = [] #订单id列表

        def assign(self,data):
            if isinstance(data.get('result'),list):
                self.value = data.get('result')
            return self

class CancelOrder(VtCancelOrderReq):
    """取消订单"""
    NAME = 'cancel_order'
    def __init__(self):
        VtCancelOrderReq.__init__(self)
        self.order_id = ''

    class Result(object):
        def __init__(self):
            self.value = False

        def assign(self,data):
            if data.get('result'):
                self.value = VtOrderData()
                self.value.__dict__ = data.get('result')
            return self

class CancelAllOrders(object):
    """取消所有订单"""
    NAME = 'cancel_all_orders'

class SellOrCoverAllTrades(object):
    """平仓所持有的仓位（平金、平⬅昨）"""
    NAME = 'sell_or_cover_all_trades'

# class StopOrderRequest(Vt)
class TradeAdapterResponseData(object):
    def __init__(self):
        self.account = ''  # 期货、股票账户名称
        self.product = ''  # 期货还是股票 feture/stock

class OnPositionData(VtPositionData,TradeAdapterResponseData):
    NAME = 'on_position_data'
    def __init__(self):
        VtPositionData.__init__(self)
        TradeAdapterResponseData.__init__(self)

class OnOrderData(VtOrderData,TradeAdapterResponseData):
    NAME = 'on_order_data'
    def __init__(self):
        VtOrderData.__init__(self)
        TradeAdapterResponseData.__init__(self)

class OnTradeData(VtTradeData,TradeAdapterResponseData):
    NAME = 'on_trade_data'
    def __init__(self):
        VtTradeData.__init__(self)
        TradeAdapterResponseData.__init__(self)

class OnAccountData(VtAccountData,TradeAdapterResponseData):
    NAME = 'on_account_data'
    def __init__(self):
        VtAccountData.__init__(self)
        TradeAdapterResponseData.__init__(self)

class GetOrder(object):
    NAME = 'get_order'
    def __init__(self):
        self.order_id = ''

    class Result(object):
        def __init__(self):
            self.value = None

        def assign(self,data):
            if data.get('result'):
                self.value = VtOrderData()
                self.value.__dict__ = data.get('result')
            return self

class GetAllWorkingOrders(object):
    NAME = 'get_all_working_orders'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.value = []

        def assign(self,data):
            if isinstance(data.get('result'),list):
                for r in data.get('result'):
                    order = VtOrderData()
                    order.__dict__ = r
                    self.value.append(order)
            return self

class GetAllOrders(GetAllWorkingOrders):
    NAME = 'get_all_orders'
    def __init__(self):
        GetAllWorkingOrders.__init__(self)


class GetAllTrades(object):
    NAME = 'get_all_trades'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.value = []

        def assign(self,data):
            if isinstance(data.get('result'),list):
                for r in data.get('result'):
                    trade = VtTradeData()
                    trade.__dict__ = r
                    self.value.append(trade)
            return self

class GetAllPositions(object):
    NAME = 'get_all_positions'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.value = []

        def assign(self,data):
            if isinstance(data.get('result'),list):
                for r in data.get('result'):
                    pos = VtPositionData()
                    pos.__dict__ = r
                    self.value.append(pos)
            return self

class GetAllAccounts(object):
    NAME = 'get_all_accounts'
    def __init__(self):
        pass

    class Result(object):
        def __init__(self):
            self.value = []

        def assign(self,data):
            if isinstance(data.get('result'),list):
                for r in data.get('result'):
                    account = VtAccountData()
                    account.__dict__ = r
                    self.value.append(account)
            return self


class StrategyLogContent(object):
    """
    策略日志级别
    """
    NAME = 'strategy_log_content'
    def __init__(self):
        self.strategy_id = ''
        self.datetime = ''
        self.timestamp = 0
        self.service_type = ''
        self.service_id = ''
        self.text = ''
        self.level = ''

    @property
    def plainText(self):
        return 'Time:{}|Strategy:{}|Text:{}'.format(self.timestamp,self.strategy_id,self.text)






