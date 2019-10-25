#coding:utf-8

from mantis.fundamental.utils.useful import hash_object,object_assign

import base
from base import INIT_NONE_VALUE, INIT_PRICE_VALUE,INIT_STRING_VALUE
import position
import order

class Constants(object):

    class DirectionType(object):
        #买卖方向类型
        Buy = '0'
        Sell = '1'

    class PositionDirection(object):
        Net = '1'
        Long = '2'
        Short = '3'

    class HedgeFlagType(object):
        Speculation = '1' #投机
        Arbitrage = '2'     # 套利
        Hedge = '3'         # 套保
        Covered = '4'       # 备兑

    class PositionDate(object):
        Today = '1'     # 今仓
        History = '2'   # 昨仓

    class TimeConditionType(object): # 有效期类型类型
        # 立即完成，否则撤销
        # simnow 委托下单时仅仅支持IOC ，即刻成交，其他时间控制均不支持
        # 实盘支持任意时间段 。
        #
        # 上期SHFE 平仓要指定平今还是平昨
        IOC = '1'
        # 本节有效
        GFS = '2'
        # 当日有效
        GFD = '3'
        # 指定日期前有效
        GTD = '4'
        # 撤销前有效
        GTC = '5'
        # 集合竞价有效
        GFA = '6'

    class VolumeConditionType(object): # 成交量类型类型
        # 任何数量
        VC_AV = '1'
        # 最小数量
        VC_MV = '2'
        # 全部数量
        VC_CV = '3'

    class ContingentConditionType(object): # 触发条件类型
        # 立即
        Immediately = '1'
        # 止损
        Touch = '2'
        # 止赢
        TouchProfit ='3'
        # 预埋单
        ParkedOrder ='4'
        # 最新价大于条件价
        LastPriceGreaterThanStopPrice ='5'
        # 最新价大于等于条件价
        LastPriceGreaterEqualStopPrice ='6'
        # 最新价小于条件价
        LastPriceLesserThanStopPrice ='7'
        # 最新价小于等于条件价
        LastPriceLesserEqualStopPrice ='8'
        # 卖一价大于条件价
        AskPriceGreaterThanStopPrice ='9'
        # 卖一价大于等于条件价
        AskPriceGreaterEqualStopPrice ='A'
        # 卖一价小于条件价
        AskPriceLesserThanStopPrice ='B'
        # 卖一价小于等于条件价
        AskPriceLesserEqualStopPrice ='C'
        # 买一价大于条件价
        BidPriceGreaterThanStopPrice ='D'
        # 买一价大于等于条件价
        BidPriceGreaterEqualStopPrice ='E'
        # 买一价小于条件价
        BidPriceLesserThanStopPrice ='F'
        # 买一价小于等于条件价
        BidPriceLesserEqualStopPrice ='H'

    class ForceCloseReason(object): # 强平原因类型
        # 非强平
        NotForceClose ='0'
        # 资金不足
        LackDeposit ='1'
        # 客户超仓
        ClientOverPositionLimit ='2'
        # 会员超仓
        MemberOverPositionLimit ='3'
        # 持仓非整数倍
        NotMultiple ='4'
        # 违规
        Violation ='5'
        # 其它
        Other ='6'
        # 自然人临近交割
        PersonDeliv ='7'
        
    class OrderPriceType(object):
        #任意价
        AnyPrice = '1'
        #限价
        LimitPrice = '2'  # simnow 仅支持限价单，其他不支持
        #最优价
        BestPrice = '3'
        #最新价
        LastPrice = '4'
        #最新价浮动上浮1个ticks
        LastPricePlusOneTicks = '5'
        #最新价浮动上浮2个ticks
        LastPricePlusTwoTicks = '6'
        #最新价浮动上浮3个ticks
        LastPricePlusThreeTicks = '7'
        #卖一价
        AskPrice1 = '8'
        #卖一价浮动上浮1个ticks
        AskPrice1PlusOneTicks = '9'
        #卖一价浮动上浮2个ticks
        AskPrice1PlusTwoTicks = 'A'
        #卖一价浮动上浮3个ticks
        AskPrice1PlusThreeTicks = 'B'
        #买一价
        BidPrice1 = 'C'
        #买一价浮动上浮1个ticks
        BidPrice1PlusOneTicks = 'D'
        #买一价浮动上浮2个ticks
        BidPrice1PlusTwoTicks = 'E'
        #买一价浮动上浮3个ticks
        BidPrice1PlusThreeTicks = 'F'
        #五档价
        FiveLevelPrice = 'G'
        #本方最优价
        BestPriceThisSide = 'H'

    #报单状态类型
    class OrderStatusType(object):
        # 全部成交
        AllTraded = '0'
        # 部分成交还在队列中
        PartTradedQueueing = '1'
        # 部分成交不在队列中
        PartTradedNotQueueing = '2'
        # 未成交还在队列中
        NoTradeQueueing = '3'
        # 未成交不在队列中
        NoTradeNotQueueing = '4'
        # 撤单
        Canceled = '5'
        # 未知
        Unknown = 'a'
        #尚未触发
        NotTouched = 'b'
        # 已触发
        Touched = 'c'

    # 是一个报单提交状态类型
    class OrderSubmitStatusType(object):
        # 已经提交
        InsertSubmitted ='0'
        # 撤单已经提交
        CancelSubmitted = '1'
        # 修改已经提交
        ModifySubmitted = '2'
        Accepted = '3'
        # 报单已经被拒绝
        InsertRejected = '4'
        # 撤单已经被拒绝
        CancelRejected = '5'
        # 改单已经被拒绝
        ModifyRejected = '6'

class AccountStat(base.AccountStat):
    """CThostFtdcTradingAccountField"""
    def __init__(self):
        base.AccountStat.__init__(self)
        self.BrokerID = ''      # 经纪公司代码
        self.AccountID = 0      # 投资者帐号
        self.Deposit = 0        # 入金金额
        self.Withdraw = 0       # 出金金额
        self.FrozenMargin = 0   # 冻结的保证金
        self.FrozenCash = 0     # 冻结的资金
        self.CurrMargin = 0     # 当前保证金总额
        self.CloseProfit = 0    # 平仓盈亏
        self.PositionProfit = 0 # 持仓盈亏
        self.Balance = 0        # 期货结算准备金
        self.Available = 0       # 可用资金
        self.WithdrawQuota = 0  # 可取资金
        self.TradingDay = 0     # 交易日
        self.SettlementID = 0   # 结算编号

    def normalize(self):
        return self


# class Price(base.Price):
class Price(base.Price):
    """标的物价格"""
    def __init__(self):
        # base.Price.__init__(self)

        self.InstrumentID = ''
        self.AveragePrice = 0  # 当日均价

        self.HighestPrice = 0       # 最高价
        self.UpperLimitPrice = 0
        self.LowerLimitPrice = 0  # 跌停板价

        self.BidPrice5 = 0   #bid 买入价
        self.BidPrice4 = 0
        self.BidPrice1 = 0
        self.BidPrice3 = 0
        self.BidPrice2 = 0

        self.OpenPrice = 0           # 今开盘

        self.PreOpenInterest = 0  # 昨持仓量
        self.Volume = 0  # 数量

        self.AskPrice5 = 0
        self.AskPrice4 = 0
        self.AskPrice3 = 0
        self.AskPrice1 = 0
        self.AskPrice2 = 0

        self.PreClosePrice = 0       # 昨收盘
        self.PreSettlementPrice = 0  # 上次结算价

        self.UpdateTime = None      # 最后修改时间
        self.UpdateMillisec = 0     # 最后修改毫秒

        self.BidVolume5 = 0
        self.BidVolume4 = 0
        self.BidVolume3 = 0
        self.BidVolume2 = 0
        self.BidVolume1 = 0

        self.AskVolume1 = 0     # 申卖量
        self.AskVolume3 = 0
        self.AskVolume2 = 0
        self.AskVolume5 = 0
        self.AskVolume4 = 0

        self.ClosePrice = 0
        self.ExchangeID = 0
        self.TradingDay = None  # 交易日
        self.PreDelta = 0
        self.OpenInterest = 0    # 持仓量
        self.CurrDelta = 0       # 今虚实度
        self.Turnover = 0       #成交金额
        self.LastPrice = 0      # 最新价
        self.SettlementPrice = 0 #本次结算价
        self.ExchangeInstID = 0 # 最高价
        self.LowestPrice = 0    # 最低价
        self.ActionDay = None
        self.DateTime = None

    @property
    def datetime(self):
        self.ActionDay = None
        self.DateTime = None
        return ''

    @property
    def last(self): # 最新成交价
        return self.LastPrice

    @property
    def qty(self): return   self.Volume  # 成交数量

    @property
    def amount(self): return   0  # 成交金额

    @property
    def total_qty(self): return   0  # 总成交量

    @property
    def total_amount(self): return   0  # 总成交额

    @property
    def yd_close(self): return   self.PreClosePrice  # 昨日收盘价

    @property
    def diff(self): return   self.LastPrice - self.PreClosePrice  # 涨跌值

    @property
    def diff_rate(self):
        return   (self.LastPrice - self.PreClosePrice)/self.PreClosePrice  # 涨跌幅率

    @property
    def sell_1(self): return self.AskPrice1

    @property
    def sell_2(self): return self.AskPrice2

    @property
    def sell_3(self): return self.AskPrice3

    @property
    def sell_4(self): return  self.AskPrice4

    @property
    def sell_5(self): return   self.AskPrice5

    @property
    def sell_qty_1(self): return   self.AskVolume1  # 量

    @property
    def sell_qty_2(self): return   self.AskVolume2  # 量

    @property
    def sell_qty_3(self): return   self.AskPrice3  # 量

    @property
    def sell_qty_4(self): return   self.AskVolume4  # 量

    @property
    def sell_qty_5(self): return   self.AskVolume5  # 量

    @property
    def buy_1(self): return   self.BidPrice1

    @property
    def buy_2(self): return   self.BidPrice2

    @property
    def buy_3(self): return   self.BidPrice3

    @property
    def buy_4(self): return   self.BidPrice4

    @property
    def buy_5(self): return   self.BidPrice5

    @property
    def buy_qty_1(self): return   self.BidVolume1  # 量

    @property
    def buy_qty_2(self): return   self.BidVolume2  # 量

    @property
    def buy_qty_3(self): return   self.BidVolume3  # 量

    @property
    def buy_qty_4(self): return   self.BidVolume4  # 量

    @property
    def buy_qty_5(self): return   self.BidVolume5  # 量



class Position(position.Position):
    """持仓记录"""
    def __init__(self):
        # position.Position.__init__(self)
        self.InstrumentID = ''
        self.PosiDirection = ''
        self.HedgeFlag = ''
        self.PositionDate = 0
        self.YdPosition = 0     # 昨苍
        self.Position = 0       # 今日总持仓 YdPosition + TodayPosition
        self.LongFrozen = 0     # 多头冻结
        self.ShortFrozen = 0    # 空头冻结
        self.LongFrozenAmount = 0   # 开仓冻结金额
        self.ShortFrozenAmount = 0  # 空仓冻结金额
        self.OpenVolume = 0     # 开仓量
        self.CloseVolume = 0    # 平仓量
        self.OpenAmount = 0     # 开仓金额
        self.CloseAmount = 0    # 平仓金额
        self.PositionCost = 0   # 持仓成本 持仓均价
        self.PreMargin = 0      # 上次占用的保证金
        self.UseMargin = 0      # 占用的保证金
        self.FrozenMargin = 0   # 冻结的保证金
        self.FrozenCash = 0     # 冻结的资金
        self.FrozenCommission = 0   # 冻结的手续费
        self.CashIn = 0         # 资金差额
        self.Commission = 0     # 手续费
        self.CloseProfit = 0    # 平仓盈亏
        self.PositionProfit = 0 # 持仓盈亏
        self.TradingDay = 0     # 交易日
        self.SettlementID = 0   # 结算编号
        self.OpenCost = 0       # 开仓成本
        self.ExchangeMargin = 0 # 交易所保证金
        self.TodayPosition = 0  # 今日持仓
        self.MarginRateByMoney = 0  # 保证金率
        self.MarginRateByVolume = 0 # 保证金率(按手数)
        self.ExchangeID = 0     # 交易所代码
        self.YdStrikeFrozen = 0 # 执行冻结的昨仓

    def normalize(self):
        self.YdPosition = int(self.YdPosition)
        self.Position = int(self.Position)
        self.LongFrozen = float(self.LongFrozen ) # 多头冻结
        self.ShortFrozen = float(self.ShortFrozen)  # 空头冻结
        self.LongFrozenAmount = float(self.LongFrozenAmount)  # 开仓冻结金额
        self.ShortFrozenAmount = float(self.ShortFrozenAmount)  # 空仓冻结金额
        self.OpenVolume = int(self.OpenVolume)  # 开仓量
        self.CloseVolume = int(self.CloseVolume)  # 平仓量
        self.OpenAmount = float(self.OpenAmount)  # 开仓金额
        self.CloseAmount = float(self.CloseAmount)  # 平仓金额
        self.PositionCost = float(self.PositionCost)  # 持仓成本 持仓均价
        self.PreMargin = float(self.PreMargin)  # 上次占用的保证金
        self.UseMargin = float(self.UseMargin)  # 占用的保证金
        self.FrozenMargin = float(self.FrozenMargin)  # 冻结的保证金
        self.FrozenCash = float(self.FrozenCash)  # 冻结的资金
        self.FrozenCommission = float(self.FrozenCommission)  # 冻结的手续费
        self.CashIn = float(self.CashIn)  # 资金差额
        self.Commission = float(self.Commission)  # 手续费
        self.CloseProfit = float(self.CloseProfit)  # 平仓盈亏
        self.PositionProfit = float(self.PositionProfit)  # 持仓盈亏
        self.TradingDay = self.TradingDay  # 交易日
        # self.SettlementID = 0  # 结算编号
        self.OpenCost = float(self.OpenCost)  # 开仓成本
        self.ExchangeMargin = float(self.ExchangeMargin)  # 交易所保证金
        self.TodayPosition = float(self.TodayPosition)  # 今日持仓
        self.MarginRateByMoney = float(self.MarginRateByMoney)  # 保证金率
        self.MarginRateByVolume = float(self.MarginRateByVolume)  # 保证金率(按手数)
        # self.ExchangeID = 0  # 交易所代码
        self.YdStrikeFrozen = float(self.YdStrikeFrozen)  # 执行冻结的昨仓
        return self

class TradeReturn(order.TradeReturn):
    def __init__(self):
        # order.TradeReturn.__init__(self)
        self.InstrumentID = ''    # 合约代码
        self.OrderRef = 0         # 报单引用
        self.UserID = ''          # 用户代码
        self.ExchangeID = ''      # 交易所代码
        self.TradeID = ''         # 成交编号
        self.Direction = ''       # 买卖方向
        self.OrderSysID = ''      # 报单编号
        self.ParticipantID = ''   # 会员代码
        self.ClientID = ''        # 客户代码
        self.TradingRole = ''     # 交易角色
        self.ExchangeInstID = ''  # 合约在交易所的代码
        self.OffsetFlag = ''      # 开平标志
        self.HedgeFlag = ''       # 投机套保标志
        self.Price = 0            # 价格
        self.Volume = 0           # 数量
        self.TradeDate = ''       # 成交时期
        self.TradeTime = ''       # 成交时间
        self.TradeType = ''       # 成交类型
        self.PriceSource = ''     # 成交价来源
        self.TraderID = ''        # 交易所交易员代码
        self.OrderLocalID = ''    # 本地报单编号
        self.ClearingPartID = ''  # 结算会员编号
        self.BusinessUnit = ''    # 业务单元
        self.SequenceNo = ''      # 序号
        self.TradingDay = ''      # 交易日
        self.SettlementID = ''    # 结算编号
        self.BrokerOrderSeq = ''  # 经纪公司报单编号
        self.TradeSource = ''     # 成交来源

    @property
    def order_id(self):
        """获取订单委托编号"""
        return 'B#{}#{}'.format(self.ExchangeID, self.OrderSysID)

    def normalize(self):
        # self.OrderSysID = self.OrderSysID.strip()
        # self.TradeID = self.TradeID.strip()
        # self.OrderLocalID = self.OrderLocalID.strip()
        return None


class OrderRecord(order.OrderRecord):
    def __init__(self):
        # order.OrderRecord.__init__(self)
        self.InstrumentID = ''          # 合约代码
        self.OrderRef       = 0         # 报单引用
        self.UserID         = ''        # 用户代码
        self.OrderPriceType = ''        # 报单价格条件
        self.Direction      = ''        # 买卖方向
        self.CombOffsetFlag = ''        # 组合开平标志
        self.CombHedgeFlag  = ''        # 组合投机套保标志
        self.LimitPrice     = 0         # 价格
        self.VolumeTotalOriginal = ''   # 数量
        self.TimeCondition  = ''        # 有效期类型
        self.GTDDate        = ''        # GTD日期
        self.VolumeCondition = ''       # 成交量类型
        self.MinVolume      = 0         # 最小成交量
        self.ContingentCondition = ''   # 触发条件
        self.StopPrice      = 0         # 止损价
        self.ForceCloseReason = ''      # 强平原因
        self.IsAutoSuspend  = ''        # 自动挂起标志
        self.RequestID      = 0         # 请求编号
        self.OrderLocalID   = ''        # 本地报单编号
        self.ExchangeID     = ''        # 交易所代码
        self.ClientID       = ''        # 客户代码
        self.OrderSubmitStatus = ''     # 报单提交状态
        self.NotifySequence = ''        # 报单提示序号
        self.TradingDay     = ''        # 交易日
        self.SettlementID   = ''        # 结算编号
        self.OrderSysID     = ''        # 报单编号
        self.OrderSource    = ''        # 报单来源
        self.OrderStatus    = ''        # 报单状态
        self.OrderType      = ''        # 报单类型
        self.VolumeTraded   = ''        # 今成交数量
        self.VolumeTotal    = ''        # 剩余数量
        self.InsertDate     = ''        # 报单日期
        self.InsertTime     = ''        # 委托时间
        self.ActiveTime     = ''        # 激活时间
        self.SuspendTime    = ''        # 挂起时间
        self.UpdateTime     = ''        # 最后修改时间
        self.CancelTime     = ''        # 撤销时间
        self.SequenceNo     = ''        # 序号
        self.FrontID        = ''        # 前置编号
        self.SessionID      = ''        # 会话编号
        self.UserProductInfo = ''       # 用户端产品信息
        self.StatusMsg      = ''        # 状态信息
        self.UserForceClose = ''        # 用户强评标志
        self.BrokerOrderSeq = ''        # 经纪公司报单编号
        self.BranchID       = ''        # 营业部编号

    @property
    def code(self):
        return self.InstrumentID

    @property
    def name(self):
        return  self.InstrumentID

    @property
    def order_id(self):
        """获取订单委托编号"""
        return 'B#{}#{}'.format(self.ExchangeID,self.OrderSysID)

    @property
    def user_order_id(self):
        """获取用户委托编号"""
        return 'A#{}#{}#{}'.format(self.FrontID, self.SessionID, self.OrderRef)

    def normalize(self):
        self.OrderStatus = chr(self.OrderStatus)
        self.OrderSubmitStatus = chr(self.OrderSubmitStatus)
        # self.OrderSysID = self.OrderSysID.strip()

    def cancelable(self):
        if self.OrderStatus  not in (Constants.OrderStatusType.AllTraded,Constants.OrderStatusType.Canceled):
            return True
        return False

class BarData(base.BarData):
    def __init__(self):
        base.BarData.__init__(self)

