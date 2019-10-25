#coding:utf-8

"""
期货行情测试

"""

import numpy as np
import talib as ta

import time

code = 'SRB1905'
logfile = 'z:/futures_simple_ma_{}.log'.format(code)
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

    pos_list = Strategy.Product.F_Pos
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

ma_buy_count = 0
ma_sell_count = 0

def strategy_ma( stk ):
    """计算均线策略"""
    global ma_buy_count,ma_sell_count

    close = getHistoryBars(stk,'1m',limit=30)
    # println(bars)
    # close = map(lambda _:_.Close,bars)

    close = np.array(close)
    println( 'size:%s'%len(close))

    println('to ma calculating...')

    ma5 = ta.MA(close, 5)

    ma10 = ta.MA(close, 10)

    a, b = ma5[-2:]
    c, d = ma10[-2:]

    # strategy_name = 'strategy_ma'
    println( 'ma5:', ma5)
    println('ma10:', ma10)
    # self.logger.debug('=={}=={}=='.format(code, interval))
    println('(strategy_ma) ma5:{}'.format(ma5.tolist()))
    println('(strategy_ma) ma10:{}'.format(ma10.tolist()))

    println('(strategy_ma）a:{} b:{} c:{} d:{}'.format(a, b, c, d))

    last_price = stk.KnockPrice  # 最近价格

    if b >= d and a < c and ma_buy_count == 0:
        num = 100
        println('strategy_ma, (b >= d and a< c), a:{} b:{} c:{} d:{}'.format(a, b, c, d))

        amount = Strategy.Product.Fut_UseableAmt  # 获取可用资金数


        cost = last_price * num
        if cost <= amount * 0.1:
            println('do buy: {} , {} , {}'.format(code, last_price, num))

            order = OrderItem(code, 'B', num, last_price,oc = 'O')
            order_id = Strategy.Order(order)

            ma_buy_count = 1

    if b <= d and a > c and ma_sell_count == 0:
        num = 100
        println('strategy_ma, (b <=d and a > c), a:{} b:{} c:{} d:{}'.format(a, b, c, d))

        pos = getPosition(code)

        if num <= pos.TdQty:
            println('do sell: {} ,{}, {}'.format(code, last_price, num))

            order = OrderItem(code, 'S', num, last_price)
            order_id = Strategy.Order(order)

            ma_sell_count= 1


def start(market,strategy,orderitem):
    global Market,Strategy,OrderItem
    Market = market
    Strategy = strategy
    OrderItem = orderitem

    stk = Market.Stk(code)
    stk.OnTick += on_tick
    # stk.MinuteData15.OnNewBar += on_bar
    stk.MinuteData1.OnNewBar += on_bar
    stk.Product.Changed += on_product_changed
    println('Strategy started..')

    # strategy_ma(stk)

def on_product_changed():
    pass

def on_tick(stk):
    println( time.asctime(stk.KnockTime), stk.KnockPrice )
    pass

def on_bar(kdata,num):
    bar = kdata[num]
    stk = kdata.Stk
    println( bar.DateTime,bar.Close)
    # strategy_ma(stk)


"""
import sys
import os 
import time
import threading
import ctypes

sys.path.append('F:/Projects/Branches')
import mantis.sg.fisher.strepo.ams.futures.quotes as module

module.start(Market,Strategy,OrderItem)

"""