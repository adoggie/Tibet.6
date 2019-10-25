#coding:utf-8

"""
simple ma

简单均线买卖
"""

import numpy as np
import talib as ta

import time

code = '0600000'
# code = '0600776'
# code = '1002129'
code = '0600834'
code = '1300252'  # 金信诺
code = '1300310'  # 金信诺

logfile = 'z:/zf_inday/{}.log'.format(code)
log = open(logfile,'a+')


Market = None
Strategy = None
OrderItem = None

def getHistoryBars(stk, cycle='1m', limit=100, inc_last=False):
    """获取历史k线
    剔除最后一根活动k线(盘中不能使用最后一根k线，或许是未完成计算的中间结果)
    result 以时间升序排列
    """
    bars = {'1m': stk.MinuteData1, '5m': stk.MinuteData5, '15m': stk.MinuteData15, '30m': stk.MinuteData30,
        'd': stk.DailyData, 'w': stk.WeeklyData, 'm': stk.MonthlyData, 'q': stk.QuarterlyData, 'y': stk.YearlyData}
    result = []
    kdata = bars.get(cycle)
    max = kdata.Count
    offset = 0
    if not inc_last:
        offset = -1
    # print max - limit + offset, max + offset
    for num in range(max - limit + offset, max + offset):  # 不包含最后一根
        d = kdata[num]
        # bar = stbase.BarData()
        # bar.close = d.Close
        result.append(d.Close)
        # print d.Close
    return result


def getPosition( code):
    """查询指定 股票代码或者指定策略的持仓记录"""

    pos_list = Strategy.Product.S_Pos
    for _ in pos_list:
        if _.ServerCode == code:
            return _
    return None

def println(*args):
    text = str( time.asctime() )
    for _ in args:
        text += ' '+str(_)
    text += '\n'
    log.write(text)
    log.flush()
    print text

buy_count = 0
sell_count = 0

buy_order_id = None
sell_order_id = None


class OrderRequest(object):
    Buy = 'long'
    Sell = 'short'
    Open = 'open'
    Cover = 'cover'

    def __init__(self,code='',price=0,num=0,order_id=0,direction=Buy,oc=Open):
        self.code = code
        self.price = price
        self.num = num
        self.order_id = order_id
        self.direction = direction
        self.oc = oc
        self.min_knock_num_rate = 0.5 # 最小

current_order_req = None

count = 0
def zf_inday( stk, num=200, limit=0.01) :
    """日内涨跌幅策略
        @:param code: 股票代码
        @:param num ：买卖数量
        @:param limit: 价格浮动限

        当日仅仅允许买卖各触发一次

    """
    global buy_count,sell_count,buy_order_id,sell_order_id
    global current_order_req
    global  count

    # zf = stk.KnockPrice / stk.ClosePrice - 1
    zf = stk.DiffRate
    st_price = stk.ClosePrice * (1 + limit)
    st_price = round(st_price, 2)

    println('price:',stk.KnockPrice,'last:',stk.ClosePrice,'zf:',zf,'limit:',limit)
    if zf <= -limit:

        # 跌幅过限
        amount = Strategy.Product.Stk_UseableAmt # self.st.product.getAmountUsable()
        st_price = stk.SellPrice1

        # println('strategy_inday, (zf <= -limit), zf:%s , st_price:%s' %(zf, st_price))

        pos = getPosition(code)
        if not pos:
            println('yd pos is 0. Exit..')
            Strategy.Exit()
            return
        #
        if pos.PostCostAmt <= amount * 0.1 and not buy_order_id :
            """持仓资金占总资金 <= 10% """
            println('do buy: {} ,{}, {}'.format(code, st_price, num))

            order = OrderItem(code, 'B', num, st_price)
            order_id = Strategy.Order(order)
            buy_order_id = order_id
            current_order_req = OrderRequest(code,st_price,num,order_id,OrderRequest.Buy,OrderRequest.Open)


    elif zf >= limit:

        st_price = stk.BuyPrice1
        println('strategy_inday, (zf >= limit), zf:%s st_price:%s ' %(zf, st_price))

        pos = getPosition(code)
        if not pos:
            println('yd pos is 0. Exit..')
            Strategy.Exit()
            return
        # print pos.YdQty
        if pos.YdQty >= num and not sell_order_id:
            println('do sell: {} ,{}, {}'.format(code, st_price, num))
            order = OrderItem(code, 'S', num, st_price)
            order_id = Strategy.Order(order)
            sell_order_id = order_id
            current_order_req = OrderRequest(code, st_price, num, order_id, OrderRequest.Sell, OrderRequest.Open)

    if current_order_req:
        order = None
        println('query order:',current_order_req.order_id)
        orders = Strategy.GetOrdersByOrigSerialNo(current_order_req.order_id)
        println('orders size:',len(orders))

        if orders:
            order = orders[0]
        if order:
            println('knockqty:',order.KnockQty)
            if order.KnockQty >= current_order_req.min_knock_num_rate * current_order_req.num:
                if current_order_req.direction == OrderRequest.Buy:
                    sell_order_id = '' #  允许开卖
                if current_order_req.direction == OrderRequest.Sell:
                    buy_order_id = ''
                current_order_req = None
                count += 1
        # else:
        #     current_order_req = None


            # if order.StatusCode == 'Fully_Filled':



def start(market,strategy,orderitem):
    global Market,Strategy,OrderItem
    Market = market
    Strategy = strategy
    OrderItem = orderitem

    stk = Market.Stk(code)
    stk.OnTick += on_tick
    # stk.MinuteData15.OnNewBar += on_bar
    stk.MinuteData1.OnNewBar += on_bar

    println('Strategy started..')

    # strategy_ma(stk)

def on_tick(stk):
    # println( time.asctime(stk.KnockTime), stk.KnockPrice )
    zf_inday(stk)
    if count >= 6:
        Strategy.Exit()

def on_bar(kdata,num):
    bar = kdata[num]
    stk = kdata.Stk
    # println( bar.DateTime,bar.Close)
    # strategy_ma(stk)


"""
import sys
import os 
import time
import threading
import ctypes

sys.path.append('F:/Projects/Branches')
import mantis.sg.fisher.strepo.ams.zf_inday as module

module.start(Market,Strategy,OrderItem)

"""