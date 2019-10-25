#coding:utf-8


"""
mongodb api ref:
https://docs.mongodb.com/manual/reference/method/db.collection.find/
"""
from collections import OrderedDict
import pymongo
from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
from dateutil.parser import parse
from dateutil.rrule import *
from functools import partial
from mantis.trade.types import ProductClass,TimeDuration
from vnpy.trader.vtObject import VtTickData,VtBarData
from mantis.trade.utils import get_symbol_prefix
from mantis.trade.trade_time import get_trade_timespace_by_product,\
    get_trade_timespace_by_exchange,is_trade_day,get_timespace_of_trade_day
import copy

CTP_TICK_DB = 'Ctp_Tick'
CTP_BAR_DB = 'Ctp_Bar_{}'

mongodb_conn = None
symbol_min_dict = OrderedDict() # { 'AP901':Set(DateTime(09,00),..) }

ts = list(rrule(MINUTELY,interval=1,dtstart=parse('2013-08-01 9:0'),until=parse('2013-08-01 10:45 ')))#间隔为3



def get_trade_timetable_template(symbol,productCls = ProductClass.Future):
    product = symbol
    if len(symbol) > 3:
        product = get_symbol_prefix(symbol)
    return get_trade_timespace_by_product(product)

def time_work_right_short(spaces,t):
    """
    考虑 开市前的1分钟集合竞价，每个交易尾端延时1分钟缓冲 '*'， 跨日'-'时段不考虑尾端延长

    """
    t = t.time()
    for space in spaces:

        if space[1] == Time(0,0) and t >=space[0]:
            return space
        e = (DateTime.combine(DateTime.now().date(), space[1]) + TimeDelta(minutes=1)).time()
        if t >= space[0] and t < e:  #  包含右侧结束时间(保持1分钟数据接收缓冲)
            return space
        if len(space) == 3 and space[-1].count('*'): # 时间段开始包括 1分钟的集合竞价时间
            s = (DateTime.combine( DateTime.now().date(),space[0]) - TimeDelta(minutes=1)).time()

            if t >= s  and t < e:
                return space
    return ()


def time_work_right_short_hour(spaces,t):
    """
    考虑 开市前的1分钟集合竞价，每个交易尾端延时1分钟缓冲 '*'， 跨日'-'时段不考虑尾端延长

    """
    t = t.time()
    for space in spaces:

        if space[1] == Time(0,0) and t >=space[0]:
            return space
        e = (DateTime.combine(DateTime.now().date(), space[1]) + TimeDelta(minutes=1)).time()
        if t.hour >= space[0].hour and t.hour <= space[1].hour:
            return space
        if t >= space[0] and t < e:  #  包含右侧结束时间(保持1分钟数据接收缓冲)
            return space
        # if len(space) == 3 and space[-1].count('*'): # 时间段开始包括 1分钟的集合竞价时间
        #     s = (DateTime.combine( DateTime.now().date(),space[0]) - TimeDelta(minutes=1)).time()
        #
        #     if t >= s  and t < e:
        #         return space
    return ()

# def time_work_right_close(spaces,t):
#     t = t.time()
#     for space in spaces:
#          if t >= space[0] and t <= space[1]:
#                 return True
#     return False

def get_day_trade_minute_line(product,date):
    """
    返回一天内指定合约交易时段内所有分钟计算点
    最后一分钟没有交易
    :param symbol:
    :param date: DateTime
    :return:
    """
    entries = get_trade_timetable_template(product)
    result = []
    for w in range(len(entries)):
        s,e = entries[w][:2]
        dts = DateTime(date.year,date.month,date.day,s.hour,s.minute,s.second)
        dte = DateTime(date.year,date.month,date.day,e.hour,e.minute,e.second) # - TimeDelta(minutes=1)
        if len(entries[w]) ==  3 and entries[w][-1].count('-'): # 跨天
            dts+=TimeDelta(days=1)
            dte+=TimeDelta(days=1)
        else:
            if dte < dts: # 跨天的行情
                dte = dte + TimeDelta(days=1)
        dte-=TimeDelta(minutes=1) # 不包括收尾分钟
        mins = list(rrule(MINUTELY, interval=1, dtstart=dts, until=dte))
        result+=mins
    return result

def get_day_trade_calc_minutes(product,date):
    """
    计算当日1分钟触发k线计算的分钟点
    包含： 开盘-收盘的交易分钟推迟1分钟 ，
    例如： 9：01 触发计算 9：00 分钟k线，
           10：16 触发计算 10:14 分钟k线

    """
    entries = get_trade_timetable_template(product)
    result = []
    for w in range(len(entries)):
        s, e = entries[w][:2]
        dts = DateTime(date.year, date.month, date.day, s.hour, s.minute, s.second)
        dte = DateTime(date.year, date.month, date.day, e.hour, e.minute, e.second)  # - TimeDelta(minutes=1)
        if len(entries[w]) == 3 and entries[w][-1].count('-'):  # 跨天
            dts += TimeDelta(days=1)
            dte += TimeDelta(days=1)
        else:
            if dte < dts:  # 跨天的行情
                dte = dte + TimeDelta(days=1)

        mins_norm = list(rrule(MINUTELY, interval=1, dtstart=dts, until=dte))
        del mins_norm[-1]

        # 开盘延后1分钟，收盘延后一分钟
        dts += TimeDelta(minutes=1)
        if e != Time(0,0):
            dte += TimeDelta(minutes=1)  # 不包括收尾分钟

        mins = list(rrule(MINUTELY, interval=1, dtstart=dts, until=dte))

        if e != Time(0, 0):
            del mins[-2]

        min_set = []
        print len(mins),len(mins_norm)
        for n in range(len(mins)):
            min_set.append([mins_norm[n],mins[n],1]) #  交易时间，计算时间，时间跨度

        # min_set = map(lambda _:[_,1],mins)

        if e != Time(0, 0):
            # min_set[-1][1] = 2 # 尾段时间触发计算首尾  10:16 计算10：14，10：15的tick数据
            min_set[-1][2] = 2 # 尾段时间触发计算首尾  10:16 计算10：14，10：15的tick数据

        # 处理两个时段的集合竞价
        if dts.time() in (Time(9,1),Time(21,1)):
            min_set[0][2] = 2 # 9:1 计算 8:59,9:0的tick数据


        result += min_set
        # result.append('------')

    times= OrderedDict()
    """
      { 计算时间: 【交易时间,计算时间,时间跨度】 }  有效数据时间: ( 计算时间 - 跨度 => 计算时间 )
    """
    for item in result:
        times[item[1]] = item
    return times


def get_day_trade_calc_minutes_new(product,nmin,date):
    """
    计算当日1分钟触发k线计算的分钟点
    包含： 开盘-收盘的交易分钟推迟1分钟 ，
    例如： 9：01 触发计算 9：00 分钟k线，
           10：16 触发计算 10:14 分钟k线

        计算当日 9：00 到 第二日凌晨 2:30

    """
    if nmin not in (1,5,15,30,60):
        return None

    dts = DateTime(date.year, date.month, date.day, 9, 0, 0)
    dte = DateTime(date.year, date.month, date.day, 2, 30, 0)
    dte = dte + TimeDelta(days=1)

    mins = list(rrule(MINUTELY, interval=nmin, dtstart=dts, until=dte))
    # mins = map(lambda dt:dt.time().replace(second=0,microsecond=0),mins)


    entries = get_trade_timetable_template(product)
    result = OrderedDict()

    for min in mins:

        for w in range(len(entries)):
            s, e = entries[w][:2]
            dts = DateTime(date.year, date.month, date.day, s.hour, s.minute, s.second)
            dte = DateTime(date.year, date.month, date.day, e.hour, e.minute, e.second)  # - TimeDelta(minutes=1)

            if e == Time(0,0):
                dte = dte + TimeDelta(days=1)

            if s == Time(0,0):
                dts += TimeDelta(days=1)
                dte += TimeDelta(days=1)
            # dte = dte -  TimeDelta(minutes=1)

            if min >= dts and min < dte:
                pass
            else:
                continue

            # 1 分钟 时间刻度
            if nmin == 1:
                trade_time = min
                calc_time = min + TimeDelta(minutes=1)
                time_span = nmin

                if min.time() in (Time(9, 0), Time(21, 0)):
                    time_span = nmin + 1

                if min == (dte - TimeDelta(minutes=1)) and min.time()!=Time(23,59): # 10:14 => 10:16 , 2
                    time_span = nmin + 1
                    calc_time = min + TimeDelta(minutes=2)
                result[calc_time] = [trade_time,calc_time,time_span]
            else:#
                trade_time = min
                calc_time = min + TimeDelta(minutes=nmin)
                time_span = nmin

                if min.time() in (Time(9, 0), Time(21, 0)):
                    time_span = nmin + 1

                if min + TimeDelta(minutes=nmin) == dte \
                        and (dte-TimeDelta(minutes=1)).time()!=Time(23,59):

                # if min.time()!=Time(23,59): #
                #     print min
                    time_span = nmin+1
                    calc_time = min + TimeDelta(minutes=nmin+1)

                result[calc_time] = [trade_time, calc_time, time_span]

    """
      { 计算时间: 【交易时间,计算时间,时间跨度】 }  有效数据时间: ( 计算时间 - 跨度 => 计算时间 )
    """
    return result


def get_day_trade_nminute_line(product,nmin,date):
    """
    返回一天内指定合约交易时段内指定n分钟间隔的时间计算点
    最后一分钟没有交易
    nmin - 3m 5m 15m 30m 60m
    """
    result = []
    if nmin not in (3,5,15,30,60):
        return result

    entries = get_trade_timetable_template(product)

    for w in range(len(entries)):
        s, e = entries[w][:2]
        smin = emin = 0
        # if s.minute:
        if 1:
            smin = s.minute/nmin*nmin
        # if e.minute:
        if 1:
            mp = e.minute % nmin
            if mp:
                emin = (e.minute/nmin+1)*(nmin)
                emin -=1
            else:
                emin = (e.minute / nmin) * (nmin)
                emin = e.minute -1

            # if emin:
            #     emin-=1
            # else:
            #     emin =59
                # e = e -TimeDelta(hours=1)

        dts = DateTime(date.year,date.month,date.day,s.hour,s.minute,s.second)
        dte = DateTime(date.year,date.month,date.day,e.hour,e.minute,e.second) #- TimeDelta(minutes=1)
        if len(entries[w]) ==  3 and entries[w][-1].count('-'): # 跨天
            dts+=TimeDelta(days=1)
            dte+=TimeDelta(days=1)
        else:
            if dte < dts: # 跨天的行情
                dte = dte + TimeDelta(days=1)

        dts = dts.replace(minute=smin,second=0,microsecond=0)

        if emin == -1 :
            # emin = 59
            dte = dte.replace(minute=59, second=0, microsecond=0)
            dte = dte - TimeDelta(hours=1)
        else:
            dte = dte.replace(minute=emin,second=0,microsecond=0)
        # if emin == -1:
        #     dte = dte - TimeDelta(hours=1)
        # if nmin!=60:
        # dte += TimeDelta(minutes=nmin)
        # if True:
        #     dte -= TimeDelta(minutes=1)
        mins = list(rrule(MINUTELY, interval=nmin, dtstart=dts, until=dte))  # 间隔为3

        for min in mins:
            if result.count(min) == 0:
                result.append(min)
        # result+=mins
    return result


def _get_day_trade_nminute_line(product,nmin,date):
    """
    返回一天内指定合约交易时段内指定n分钟间隔的时间计算点
    最后一分钟没有交易
    nmin - 3m 5m 15m 30m 60m
    """
    result = []
    if nmin not in (3,5,15,30,60):
        return result

    entries = get_trade_timetable_template(product)

    for w in range(len(entries)):
        s, e = entries[w][:2]
        smin = emin = 0
        if s.minute:
            smin = s.minute/nmin*nmin
        if e.minute:
            emin = e.minute/nmin*nmin
        dts = DateTime(date.year,date.month,date.day,s.hour,s.minute,s.second)
        dte = DateTime(date.year,date.month,date.day,e.hour,e.minute,e.second) #- TimeDelta(minutes=1)
        if len(entries[w]) ==  3 and entries[w][-1].count('-'): # 跨天
            dts+=TimeDelta(days=1)
            dte+=TimeDelta(days=1)
        else:
            if dte < dts: # 跨天的行情
                dte = dte + TimeDelta(days=1)

        dts = dts.replace(minute=smin,second=0,microsecond=0)
        dte = dte.replace(minute=emin,second=0,microsecond=0)
        if nmin!=60:
            dte -= TimeDelta(minutes=1)
        mins = list(rrule(MINUTELY, interval=nmin, dtstart=dts, until=dte))  # 间隔为3

        for min in mins:
            if result.count(min) == 0:
                result.append(min)
        # result+=mins
    return result


# def get_day_untrade_timerange(symbol,date):
#     """
#     返回一天内指定合约非交易时段内, 存在跨日时间
#     :param symbol:
#     :param date: DateTime
#     :return:
#     """
#     entries = get_trade_timetable_template(symbol)
#     result = []
#     zero = Time(0,0)
#     first = entries[0]
#     if zero != first[0]:
#         result.append( [zero,first[0]] )
#
#     gaps =[]
#     def _collect(result, x, y):
#         result.append([x[1],y[0]])
#         return y
#
#     reduce(partial(_collect, gaps), entries)
#     result+=gaps
#     last = entries[-1]
#     # if zero<= last[1]:
#     if zero == last[1] or last[1] >= last[0]: # 在一天之内
#         result.append( [last[1],zero] )
#     else: # 最后一项跨天了，忽略
#         pass
#
#
#     result = map(lambda _:
#                  [DateTime(date.year,date.month,date.day,_[0].hour,_[0].minute),
#                   DateTime(date.year, date.month, date.day, _[1].hour, _[1].minute)],
#                  result)
#     return result

# filter(partial(time_work,space_templetes['FUTURES_1']),ts)
#
# def is_trade_time(symbol,t,product = ProductClass.Future):
#     space = get_trade_timetable_template(symbol)
#     return time_work_right_open(space,t)
#
# def kline_make_prev_min_futures(symbol,t):
#     """
#     倒推一分钟开始计算分钟kline
#     :param symbol:
#     :param t:
#     :return:
#     """
#     # space = get_trade_timetable_template(symbol)
#     t = t - TimeDelta(minutes=1)
#     if not is_trade_time(symbol,t):
#         return
#
#     kline_make_min_futures(symbol,t)

def make_min_bar(symbol,t,nmin='1m',leftMargin=0,rightMargin=0,drop =True,product=ProductClass.Future):
    """
    开始计算指定开始分钟的 bar
    :drop  是否删除存在的分钟 bar

    1. 指定的分钟内没有tick数据
        取前一根有效的bar
        如果前无bar，则忽略本次bar计算

    """

    if nmin not in TimeDuration.SCALES.keys():
        print 'Error: paramter nmin:{} invalid.'.format(nmin)
        return
    mins = TimeDuration.SCALES[nmin]/TimeDuration.MINUTE
    t1 = t.replace(second=0,microsecond=0)
    t2 = t1 + TimeDelta(minutes=mins)
    conn = mongodb_conn
    dbname = CTP_TICK_DB
    coll = conn[dbname][symbol]

    p1 = t1 - TimeDelta(minutes=leftMargin)
    p2 = t2 + TimeDelta(minutes=rightMargin)

    rs = coll.find({'datetime':{'$gte':p1,'$lt':p2},'flag':0}).sort( (['datetime',pymongo.ASCENDING],['seq',pymongo.ASCENDING]))
    print symbol, p1, '-->', p2  #, ' count:',rs.count()
    dbname = CTP_BAR_DB
    collbar_1m = conn[dbname.format(nmin)][symbol]
    bar = None

    # return
    # 删除已存在 1m bar
    if drop:
        collbar_1m.remove({'datetime':t1})

    if rs.count() == 0: # 分钟内无tick数据 ，将连续之前的bar
        # if not prev_bar: #查找前一个bar
        prev_bar = None
        r = collbar_1m.find({'datetime':{'$lt':t1},'flag':0}).sort('datetime',pymongo.DESCENDING).limit(1)
        if r.count() :
            prev_bar = VtBarData()
            prev_bar.__dict__ = r[0]

        if prev_bar:
            prev_bar.datetime = t1
            prev_bar.date = prev_bar.datetime.strftime('%Y%m%d')
            prev_bar.time = prev_bar.datetime.strftime('%H:%M:%S.%f')
            prev_bar.high = prev_bar.close
            prev_bar.low = prev_bar.close
            prev_bar.open = prev_bar.close
            prev_bar.volume = 0
            bar = prev_bar
    else: # 计算当前分钟内的bar
        if t.hour== 21:
            print 'hour:',21
        bar = VtBarData()
        tick = VtTickData()
        tick.__dict__ = rs[0]
        bar.datetime = t1
        bar.date = bar.datetime.strftime('%Y%m%d')
        bar.time = bar.datetime.strftime('%H:%M:%S.%f')
        bar.vtSymbol = tick.vtSymbol
        bar.symbol = tick.symbol
        bar.exchange = tick.exchange
        bar.open = tick.lastPrice
        bar.high = tick.lastPrice
        bar.low = tick.lastPrice
        last = None
        #找到前一个k线最后一个tick作为last
        rs = list(rs)
        # first = rs[0]
        first = copy.deepcopy(rs[0])
        if t.time() == Time(14,59) and nmin=='1m':
            print 'pause'
        first_time = first['datetime'].time().replace(second=0,microsecond=0)
        if first_time in (Time(20,59),Time(21,0)):
            first['volume'] = 0
            last = VtTickData()
            last.__dict__ = first
            # last = first
        # if t.time()== Time(21,0):
        #     pass
        else:
            _rs = coll.find({'datetime': {'$lt': p1}, 'flag': 0}).sort((['datetime', pymongo.DESCENDING], ['seq', pymongo.DESCENDING])).limit(1)
            try:
                last = VtTickData()
                last.__dict__ = _rs[0]
            except:
                last = None

        # if _rs.count():  # too slowly, never use..
        #     last = VtTickData()
        #     last.__dict__ = _rs[0]
        # --
        # ss = list(rs)
        # s = ss[-1]
        # print s
        # return
        """
        if t.time() == Time(21,9):
            print t.time()
            rs = list(rs)
            f = open('test.txt','w')
            for s in rs:
                f.write('time:{} lower-price:{}\n'.format(str(t),s['lowPrice']))
            f.close()
        """
        for r in rs:
            tick = VtTickData()
            tick.__dict__ = r
            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)

            bar.close = tick.lastPrice
            bar.openInterest = tick.openInterest
            if last:
                bar.volume += (tick.volume - last.volume)
            last = tick
            # print bar.volume
    if bar: #写入bar
        dict_ = bar.__dict__
        if dict_.has_key('_id'):
            del dict_['_id']
        collbar_1m.insert_one(dict_)
        print 'Write {} Bar:'.format(nmin),bar.__dict__
    return bar

def make_min_bar_real_calc(symbol,nmin,kline_time,start,end,drop =True,product=ProductClass.Future):
    """
    """

    # if nmin not in TimeDuration.SCALES.keys():
    #     print 'Error: paramter nmin:{} invalid.'.format(nmin)
    #     return
    # mins = TimeDuration.SCALES[nmin]/TimeDuration.MINUTE
    # t1 = t.replace(second=0,microsecond=0)
    # t2 = t1 + TimeDelta(minutes=mins)
    conn = mongodb_conn
    dbname = CTP_TICK_DB
    coll = conn[dbname][symbol]

    # p1 = t1 - TimeDelta(minutes=leftMargin)
    # p2 = t2 + TimeDelta(minutes=rightMargin)
    t1 = kline_time
    p1 = start
    p2 = end
    rs = coll.find({'datetime':{'$gte':p1,'$lt':p2},'flag':0}).sort( (['datetime',pymongo.ASCENDING],['seq',pymongo.ASCENDING]))
    print symbol, p1, '-->', p2  #, ' count:',rs.count()
    dbname = CTP_BAR_DB
    collbar_1m = conn[dbname.format(nmin)][symbol]
    bar = None

    # return
    # 删除已存在 1m bar
    if drop:
        collbar_1m.remove({'datetime':t1})

    if rs.count() == 0: # 分钟内无tick数据 ，将连续之前的bar
        # if not prev_bar: #查找前一个bar
        prev_bar = None
        r = collbar_1m.find({'datetime':{'$lt':t1},'flag':0}).sort('datetime',pymongo.DESCENDING).limit(1)
        if r.count() :
            prev_bar = VtBarData()
            prev_bar.__dict__ = r[0]

        if prev_bar:
            prev_bar.datetime = t1
            prev_bar.date = prev_bar.datetime.strftime('%Y%m%d')
            prev_bar.time = prev_bar.datetime.strftime('%H:%M:%S.%f')
            prev_bar.high = prev_bar.close
            prev_bar.low = prev_bar.close
            prev_bar.open = prev_bar.close
            prev_bar.volume = 0
            bar = prev_bar
    else: # 计算当前分钟内的bar

        bar = VtBarData()
        tick = VtTickData()
        tick.__dict__ = rs[0]
        bar.datetime = t1
        bar.date = bar.datetime.strftime('%Y%m%d')
        bar.time = bar.datetime.strftime('%H:%M:%S.%f')
        bar.vtSymbol = tick.vtSymbol
        bar.symbol = tick.symbol
        bar.exchange = tick.exchange
        bar.open = tick.lastPrice
        bar.high = tick.lastPrice
        bar.low = tick.lastPrice
        last = None
        #找到前一个k线最后一个tick作为last
        rs = list(rs)
        # first = rs[0]
        #first = copy.deepcopy(rs[0])
        #if t.time() == Time(14,59) and nmin=='1m':
        #    print 'pause'
        #first_time = first['datetime'].time().replace(second=0,microsecond=0)
        if t1 == Time(21,0):
            bar.volume = 0

        #if first_time in (Time(20,59),Time(21,0)):
         #   first['volume'] = 0
          #  last = VtTickData()
          #  last.__dict__ = first
            # last = first
        # if t.time()== Time(21,0):
        #     pass
        #else:
        _rs = coll.find({'datetime': {'$lt': p1}, 'flag': 0}).sort((['datetime', pymongo.DESCENDING], ['seq', pymongo.DESCENDING])).limit(1)
        try:
            last = VtTickData()
            last.__dict__ = _rs[0]
        except:
            last = None
        if last and t1 == Time(21,0):
            last.volume = 0

        # if _rs.count():  # too slowly, never use..
        #     last = VtTickData()
        #     last.__dict__ = _rs[0]
        # --
        # ss = list(rs)
        # s = ss[-1]
        # print s
        # return
        """
        if t.time() == Time(21,9):
            print t.time()
            rs = list(rs)
            f = open('test.txt','w')
            for s in rs:
                f.write('time:{} lower-price:{}\n'.format(str(t),s['lowPrice']))
            f.close()
        """
        for r in rs:
            tick = VtTickData()
            tick.__dict__ = r
            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)

            bar.close = tick.lastPrice
            bar.openInterest = tick.openInterest
            if last:
                bar.volume += (tick.volume - last.volume)
            last = tick
            # print bar.volume
    if bar: #写入bar
        dict_ = bar.__dict__
        if dict_.has_key('_id'):
            del dict_['_id']
        collbar_1m.insert_one(dict_)
        print 'Write {} Bar:'.format(nmin),bar.__dict__
    return bar


def make_day_bar(symbol,date,drop =True,product=ProductClass.Future):
    """
    计算日线
    """
    from logging import getLogger

    if isinstance(date,str):
        date = parse(date)
    today = date.replace(hour=0,minute=0,second=0,microsecond=0)
    # 前一天晚上21:00  到 15:30
    # 从 1m k线计算日线
    start = today - TimeDelta(days=1)
    start = start.replace(hour=21,minute=0,second=0,microsecond=0)
    end = today.replace(hour=15,minute=0,second=0,microsecond=0)


    # days = get_timespace_of_trade_day(date)
    # bar = None
    # if not days:
    #     getLogger().info("day span is None")
    #     return None
    # t1,t2 = days

    conn = mongodb_conn
    dbname = 'Ctp_Bar_1m'
    coll = conn[dbname][symbol]

    rs = coll.find({'datetime':{'$gte':start,'$lte':end}}).sort( (['datetime',pymongo.ASCENDING],))
    print symbol, start, '-->', end, ' count:',rs.count()
    dbname = CTP_BAR_DB
    collbar = conn[dbname.format('1d')][symbol]

    bar = None
    # 删除已存在 bar
    if drop:
        collbar.remove({'datetime':today})
    # 注意，记录的日期是日盘交易的日期
    if rs.count() == 0: # 过去日内无分钟k线
        # if not prev_bar: #查找前一个bar
        prev_bar = None
        # 取上一个交易日的日Bar
        r = collbar.find({'datetime':{'$lt':today}}).sort('datetime',pymongo.DESCENDING).limit(1)
        if r.count() :
            prev_bar = VtBarData()
            prev_bar.__dict__ = r[0]

        if prev_bar:
            prev_bar.datetime = date
            prev_bar.date = prev_bar.datetime.strftime('%Y%m%d')
            prev_bar.time = prev_bar.datetime.strftime('%H:%M:%S.%f')
            prev_bar.high = prev_bar.close
            prev_bar.low = prev_bar.close
            prev_bar.open = prev_bar.close
            prev_bar.volume = 0
            bar = prev_bar
    else: # 计算当前日内的bar
        bar = VtBarData()
        minbar = VtBarData()
        minbar.__dict__ = rs[0]
        bar.datetime = today
        bar.date = bar.datetime.strftime('%Y%m%d')
        bar.time = bar.datetime.strftime('%H:%M:%S.%f')
        bar.vtSymbol = minbar.vtSymbol
        bar.symbol = minbar.symbol
        bar.exchange = minbar.exchange
        bar.open = minbar.open
        bar.high = minbar.high
        bar.low = minbar.low

        last = None

        # 找到前一个日bar最后一个 min Bar 作为last
        _rs = coll.find({'datetime': {'$lt': start} }).sort((['datetime', pymongo.DESCENDING],)).limit(1)
        try:
            last = VtBarData()
            last.__dict__ = _rs[0]
        except:
            last = None

        for r in rs:
            minbar = VtBarData()
            minbar.__dict__ = r
            bar.high = max(bar.high, minbar.high)
            bar.low = min(bar.low, minbar.low)

            bar.close = minbar.close
            bar.openInterest = minbar.openInterest
            # if last:
            if minbar.datetime.time()==Time(21,0):
                minbar.volume = 0  #
            bar.volume = bar.volume + minbar.volume
            # print minbar.volume
            last = minbar
    if bar: #写入bar
        dict_ = bar.__dict__
        if dict_.has_key('_id'):
            del dict_['_id']
        collbar.insert_one(dict_)
        print 'Write {} Bar:'.format(str(date.date())),bar.__dict__
    return bar


min_bar_made_history={}

def get_minbar_key(symbol,scale,time):
    time = time.replace(second=0,microsecond=0)
    key = '{}.{}.{}'.format(symbol,scale,str(time))
    return key

def _make_lastest_min_bar(symbol,test_time=None):
    """计算最近的1分钟 bar"""
    t = DateTime.now()
    if test_time:
        t = test_time
    t = t - TimeDelta(minutes=1) # 前一分钟
    key = get_minbar_key(symbol,'1m',t)
    if min_bar_made_history.has_key(key):
        return None
    min_bar_made_history[key] = 1

    spaces = get_trade_timetable_template(symbol)
    bar = None
    if time_work_right_short(spaces,t):
        bar = make_min_bar(symbol,t,drop=True)
    return bar

def make_lastest_min_bar(symbol,scale,calc_mins,test_time=None):
    """计算最近的1分钟 bar"""
    # calc_mins {计算时间: 【交易时间, 计算时间, 时间跨度】}

    t = DateTime.now().replace(second=0,microsecond=0)
    min_tuple = calc_mins.get(t) # 是否当前时间达到计算分钟点
    if not min_tuple:
        return None

    # 已到计算分钟时间
    key = get_minbar_key(symbol,scale,t)
    if min_bar_made_history.has_key(key):
        return None
    min_bar_made_history[key] = 1
    trade_time,calc_time,span = min_tuple

    start = calc_time - TimeDelta(minutes=span)
    end = calc_time
    print '== do k-line making..'
    print symbol,scale,min_tuple
    bar = make_min_bar_real_calc(symbol, scale, trade_time, start, end)

    return bar


def make_latest_nmin_bar(symbol,scale,test_time=None):
    """
    计算多分钟的bar

    """
    if scale not in TimeDuration.SCALES.keys():
        return None
    now = DateTime.now()
    if test_time:
        now = test_time
    nmin = TimeDuration.SCALES[scale] / TimeDuration.MINUTE
    # t = DateTime.now()
    # t = t - TimeDelta(minutes=1)  # 前一分钟


    t = now - TimeDelta(minutes=nmin)
    min = t.minute/nmin*nmin
    t = t.replace(minute=min,second=0,microsecond=0)

    spaces = get_trade_timetable_template(symbol)
    bar = None
    space = time_work_right_short(spaces, t)
    if space:
        key = get_minbar_key(symbol, scale, t)
        if min_bar_made_history.has_key(key):
            return  None
        min_bar_made_history[key] = 1
        print str(t)
        left = 0
        right = 1
        if len(space) == 3 and space[-1].count('*'): # 开盘集合竞价
            left = 1
        if len(space) == 3 and space[-1].count('-'): # 跨日时间
            right = 0
        bar = make_min_bar(symbol, t, scale,drop=True,leftMargin=left,rightMargin=right)
    return bar

def data_clear_days(symbol,start,end='',readonly=False):
    """
    删除指定时间范围内非交易时间段的tick数据
    """
    import logging
    logger = logging.getLogger()

    if isinstance(start,str):
        start = parse(start)
    if not end:
        end = start
    else:
        end = parse(end)
    end = end + TimeDelta(days=1)

    conn = mongodb_conn
    coll = conn[CTP_TICK_DB][symbol]

    spaces = get_trade_timetable_template(symbol)
    # print spaces
    f = open('data_clear_{}.txt'.format(str(start.date())),'w')

    if readonly:
        rs = coll.find({'datetime': {'$gte':start,'$lt':end}})
    else:
        rs = coll.find({'datetime': {'$gte':start,'$lt':end},'flag':0})
    for r in rs:
        if not time_work_right_short(spaces,r['datetime']):
            # coll.delete_one({'_id':r['_id']})
            if not readonly:
                coll.update_one(filter={'_id':r['_id']},update={'$set':{'flag':1}})
            # print 'Removed Record:',str(r['datetime'])
            logger.debug( 'Removed Record:'+ r['symbol'] +' '+ str(r['datetime']) )
            f.write("{} {} {}\n".format(r['symbol'],str(r['datetime']),str(r)))
    f.close()



if __name__ == '__main__':
    f = open('test.txt','w')
    # mins =  get_day_trade_minute_line('m1901',parse('2018-8-15'))
    mins =  get_day_trade_calc_minutes_new('cu1901',30,parse('2018-8-15'))
    ss = '\n'.join(map(lambda _: str(mins[_]),mins))
    f.write(ss)
    f.close()
    # print mins
    # print get_day_trade_nminute_line('m1901',5,parse('2018-8-15'))

    # data_clear_days('AP901','2018-7-27')