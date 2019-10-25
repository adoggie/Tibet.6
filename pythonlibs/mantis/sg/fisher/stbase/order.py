#coding:utf-8

from base import *
from position import *


class OrderRequest(object):
    """订单委托信息"""
    def __init__(self,code='',price=0,quantity=0,direction=Constants.Buy ,user_id = 'C'):
        self.product = None
        self.code =  code
        self.user = None  # 附加数据
        self.hedge = Constants.SPEC
        self.stop_price = 0     # 止盈止损价格
        self.market_order = Constants.MarketOrder.A   # 市价类别

        self.direction = direction
        self.oc = Constants.Open  # 默认买开

        self.price = price      # 交易价格
        self.quantity = quantity        # 买卖数量

        self.success = None
        self.failure = None
        self.message = ''
        self.order_id=''
        self.user_id = user_id #用户订单编号

        self.min_knock_num_rate = 1
        self.forceclose = False
        self.price_type = 0

        self.exchange_id = '' # 交易所编号 ，在CTP新sdk接口规定必须提供

        self.opts = {}

    def dict(self):
        return hash_object(self,excludes=('product','success','failure'))


class OrderReturn(object):
    """订单委托返回"""
    def __init__(self):
        self.error = Error()
        self.user = None
        self.contract_id = ''  # 合约编号
        self.order_id = '' # 订单编号
        self.code = ''
        self.product =  None

        self.request = OrderRequest()


class TradeReturn(object):
    """成交回报"""
    TypeOrderOrCancelConfirm = 0  #
    TypeOrderFilled = 1  #

    def __init__(self):
        self.type = self.TypeOrderOrCancelConfirm  #推送类型：0-委托确认，撤单成交 1-成交
        self.order_id = ''      # OrigSerialNo	"原始委托号 下单时拿到的唯一编号"	long
        self.user_id = ''       #OrigSource	自定义订单号	str
        self.protfolio_num = 0  # PortfolioNum	投资组合编码	long
        self.code = ' '         # ServerCode	商品代码	str
        self.direction = Constants.Buy # BSType	B-买入 S-卖出	str
        self.oc =Constants.Open     # OCFlag	O-开仓 C-平仓	str
        self.order_price = 0        # OrderPrice	委托价格	float
        self.order_qty = 0          # OrderQty	委托数量	int
        self.order_time = 0         # datetime, OrderTime	"委托时间 值为Python下时间戳"	float
        self.knock_time = 0         # datetime, KnockTime	"成交时间 值为Python下时间戳"	float
        self.knock_code = ''        # KnockCode	"成交编号 成交推送支持"	str
        self.knock_price = 0        # KnockPrice	"成交价格 成交推送支持"	float
        self.knock_qty = 0          # KnockQty	"成交数量 成交推送支持"	int
        self.knock_amount = 0       # KnockAmt	"成交金额 成交推送支持"	float
        self.total_withdraw_qty = 0  #TotalWithdrawQty	"撤单数量 撤单成交支持"	long
        self.total_knock_qty = 0        # TotalKnockQty	总成交数量	long
        self.total_knock_amount = 0     # TotalKnockAmt	总成交金额	float

        self.status = Constants.OrderStatus.Unknown
        """
        StatusCode
            "委托确认状态：
            Auditing 审批中
            AuditError 审批失败
            Registered 待发给三方
            Pending_Dealing 已报交易所，待成交
            Rejected 拒绝(三方或交易所)
            Pending_Cancel 撤单，待交易所确认
            Cancelled 撤单完成,没有成交
            Partially_Pending_Cancel 部分成交 ，等待撤单中
            Partially_Cancelled  部分成交，并且撤单完成
            成交状态：
            Partially_Filled
            Fully_Filled"	str
        """

    def dict(self):
        hash_object(self)





OrderStatus = OrderReturn

class OrderRecord(object):
    """委托记录,查询和委托事件返回都支持"""
    def __init__(self):
        self.user_id = ''       # 用户自定义编号
        self.trans_id = ''      # 交易编号
        self.contract_id = ''  # 合约编号
        self.order_id = ''      # 委托编号

        self.code= ''           # 证券代码
        self.name = ''          # 证券名称
        self.product = None

        self.order_time =  None     # 委托事件
        self.status = Constants.OrderStatus.Unknown

        self.direction = Constants.Buy
        self.oc = Constants.Open  # 默认买开
        self.hedge = Constants.SPEC

        self.order_price = 0  # 委托价格
        self.order_qty= 0       # 委托数量
        self.qty_filled = 0     # 成交数量
        self.qty_unfilled = 0   # 未成交数量 (挂单数量)
        self.qty_withdraw = 0   # 撤单数量

        self.error = Error()
        self.user = None

    def dict(self):
        return hash_object(self)

    def json(self):
        return json.dumps(self.dict())

    def __str__(self):

        return 'code:'+self.code + ' trans_id:'+ str(self.trans_id) + ' order_id:'+ str(self.order_id) +\
                ' order_time:'+ str(self.order_time) +  ' order_price:'+ str(self.order_price) + \
               ' order_qty:'+ str(self.order_qty) + ' qty_filled:' + str(self.qty_filled) + \
                ' direction:'+ str(self.direction) + ' oc:' + self.oc + \
                ' qty_withdraw:' + str(self.qty_withdraw)