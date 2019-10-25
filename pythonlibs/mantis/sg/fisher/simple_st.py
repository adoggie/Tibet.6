#coding:utf-8


"""
pip install tushare==1.2.10 simplejson

-- 单独运行simple_st.py 需添加如下环境变量
export LD_LIBRARY_PATH=/opt/kungfu/master/lib/yijinjing:/opt/kungfu/toolchain/boost-1.62.0/lib
export PYTHONPATH=/opt/kungfu/master/lib/wingchun
"""
import json
import numpy as np
import talib as ta
import stbase
import time
import datetime
from utils.timeutils import current_datetime_string
#import ts_get

CODE ='000001'
STOCK_LIST = [CODE]


def filter_trade_time(k):
    end = k['EndUpdateTime']
    tm = time.strptime(end,'%H:%M:%S')
    a = time.strptime('11:30:00','%H:%M:%S')
    b = time.strptime('13:00:00','%H:%M:%S')
    c = time.strptime('15:00:00','%H:%M:%S')

    if tm > a and tm < b :
        return False
    return True

def strategy_exec_bar(bars, intervals,source, rcv_time):
    """K线触发策略计算
    """
    for code, bar in bars.items():
        print code,bar
        # print hash_object(bar )
        if code == CODE : # and intervals == 5:
            strategy_ma(code)
            # strategy_inday(code,bar)

def record_signal(code,data,name=''):
    stbase.print_line(data, stdout=False)

    if name:
        name = name+'_'+code+'.signal'
        fname = stbase.TradeManager().getDataPath(name)
        data = current_datetime_string() + ' ' + data
        fp = open(fname,'a+')
        # fp.writelines([data])
        fp.write(data + '\n')
        fp.close()

def strategy_ma( code=CODE ,interval = 5):
    """计算均线策略"""
    # close = get_bars(code, interval)
    stock = stbase.TradeManager().getStock(code)
    bars = stock.get_hist_bars('m{}'.format(interval),limit=30)
    close = map(lambda _:_.Close,bars)

    close = np.array(close)
    stbase.print_line( 'size:%s'%len(close))


    # if not close:
    #     print 'error: close is null.'
    print close.tolist()

    stbase.print_line(close.tolist())
    print 'to ma calculating...'
    ma5 = ta.MA(close, 5)

    ma10 = ta.MA(close, 10)

    a,b = ma5[-2:]
    c,d = ma10[-2:]

    strategy_name ='strategy_ma'
    print 'ma5:',ma5
    print 'ma10:',ma10
    stbase.print_line('=={}=={}=='.format(code,interval) )
    stbase.print_line('(strategy_ma) ma5:{}'.format(ma5.tolist()),stdout=False)
    stbase.print_line('(strategy_ma) ma10:{}'.format(ma10.tolist()),stdout=False)

    stbase.print_line('(strategy_ma）a:{} b:{} c:{} d:{}'.format(a, b, c, d),stdout=False)

    last_price = stbase.TradeManager().getStock(code).last_price
    if b >= d and a< c:
        num = 100
        # stbase.print_line('-*'*20,stdout=False)
        # stbase.print_line('strategy_ma signal occur. (b >= d and a< c)',stdout=False)
        # stbase.print_line('a:{} b:{} c:{} d:{}'.format(a,b,c,d),stdout=False)

        record_signal(code,'-*'*20,strategy_name)
        record_signal(code,'=={}=={}=='.format(code,interval),strategy_name)
        record_signal(code,'strategy_ma signal occur. (b >= d and a< c)',strategy_name)
        record_signal(code,'a:{} b:{} c:{} d:{}'.format(a,b,c,d),strategy_name)

        amount = stbase.TradeManager().xy_proxy.get_stock_amount_useable()

        cost = last_price * num
        if cost <= amount * 0.1:
            record_signal(code,'do buy: {} , {} , {}'.format(code,last_price, num), strategy_name)
            stbase.TradeManager().xy_proxy.buy(code,last_price,num)

    if b <=d and a > c:
        num  = 100
        # stbase.print_line('-*' * 20, stdout=False)
        # stbase.print_line('strategy_ma signal occur. (b <=d and a > c)',stdout=False)
        # stbase.print_line('a:{} b:{} c:{} d:{}'.format(a, b, c, d),stdout=False)

        record_signal(code,'-*' * 20,strategy_name)
        record_signal(code,'=={}=={}=='.format(code, interval), strategy_name)
        record_signal(code,'strategy_ma signal occur.  (b <=d and a > c)',strategy_name)
        record_signal(code,'a:{} b:{} c:{} d:{}'.format(a, b, c, d),strategy_name)

        if num <= stbase.TradeManager().getStock(code).pos.net_yd:
            record_signal(code,'do sell: {} ,{}, {}'.format(code, last_price,num), strategy_name)
            stbase.TradeManager().xy_proxy.sell(code,last_price,num)

strategy_inday_buy_count = {}
strategy_inday_sell_count = {}


def strategy_inday(code,num = 100 ,limit=0.02 ):
    """日内涨跌幅策略
    @:param code: 股票代码
    @:param num ：买卖数量
    @:param limit: 价格浮动限

    当日仅仅允许买卖各触发一次

    """
    global strategy_inday_buy_count
    global strategy_inday_sell_count

    stock = stbase.TradeManager().getStock(code)

    zf =  stock.last_price / stock.yesterday_close_price - 1
    # stbase.print_line('(strategy_inday) zf:%s last_price:%s  yd_close_price:%s'%(zf,stock.last_price,stock.yesterday_close_price),stdout=False )

    stbase.print_line('=={}=='.format(code))

    strategy_name='strategy_inday'
    st_price =  stock.yesterday_close_price * (1+limit)
    st_price = round(st_price,2)
    if zf <= -limit:
        stbase.print_line('(strategy_inday) zf:%s last_price:%s  yd_close_price:%s' % (zf, stock.last_price, stock.yesterday_close_price), stdout=False)

        record_signal('=={}=='.format(code), strategy_name)
        record_signal('strategy_inday signal occur. (zf <= -limit)',strategy_name)
        record_signal('zf:{} limit:{}'.format(zf,limit),strategy_name)
        #跌幅过限
        amount = stbase.TradeManager().xy_proxy.get_stock_amount_useable()
        pos_sum = stock.pos.net_total
        #
        if stock.pos.post_cost_amount <= amount * 0.1 and strategy_inday_buy_count.get(code,0):
            """持仓资金占总资金 <= 10% """
            record_signal('do buy: {} ,{}, {}'.format(code,st_price, num), strategy_name)
            stbase.TradeManager().xy_proxy.buy(code,st_price,num)
            strategy_inday_buy_count[code]=1

    elif zf >= limit:
        """ """
        stbase.print_line('(strategy_inday) zf:%s last_price:%s  yd_close_price:%s' % (
        zf, stock.last_price, stock.yesterday_close_price), stdout=False)

        record_signal('=={}=='.format(code), strategy_name)
        record_signal('-*' * 20,'strategy_inday')
        record_signal('strategy_inday signal occur. (zf >= -limit)',strategy_name)
        record_signal('zf:{} limit:{}'.format(zf, limit),strategy_name)
        if stock.pos.net_total >= num and strategy_inday_sell_count.get(code,0):
            record_signal('do sell: {} ,{}, {}'.format(code, st_price,num), strategy_name)
            stbase.TradeManager().xy_proxy.sell(code,st_price,num)
            strategy_inday_sell_count[code]=1


print 'simple_st start ...'


if __name__ == '__main__':
    # print api.daily(ts_code='000001.SZ',trade_date='20190104')
    strategy_ma(CODE)
