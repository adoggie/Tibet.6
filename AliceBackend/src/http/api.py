#coding:utf-8

import json
import time
import datetime
import os.path
import os
from dateutil.parser import parse

from collections import OrderedDict
from flask import Flask,request,g
from flask import Response
import requests
import base64
from StringIO import StringIO

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.utils.useful import cleaned_json_data


from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import current_datetime_string,timestamp_current,timestamp_to_str,datetime_to_str
from mantis.fundamental.utils.mongo import normal_dict

from token import token_encode
from token import  login_check
from mantis.sg.fisher.model import model
from AliceBackend.errors import ErrorDefs

def hello():
    """写下第一个webapi """
    ip= request.remote_addr
    result = []
    return CR(result = result)

def get_trade_days():
    conn = instance.datasourceManager.get('mongodb').conn
    names = conn.database_names()
    names = filter(lambda _:_.find('TradeFisher_')!=-1 , names)
    names = map(lambda  _: _.split('_')[1], names)
    return CR(result= names).response

def get_strategy_list():
    date_s = request.values.get('date','')
    if not date_s:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response
    date = parse(date_s)
    conn = instance.datasourceManager.get('mongodb').conn
    dbname = 'TradeFisher_{}-{}-{}'.format(date.year,date.month,date.day)
    db = conn[dbname]
    model.StrategyParam.__database__ = db
    sts = model.StrategyParam.find()
    result = []
    for s in sts:
        s.date = date_s
        result.append( s.dict())
    return CR(result=result).response


"""
http://localhost:7788/fisher/api/strategy/code/list?date=2019-5-15&strategy_id=AJ_ZF_InDay
"""
def get_code_list():
    date = request.values.get('date', '')
    strategy_id = request.values.get('strategy_id')
    if not strategy_id or not date :
        return ErrorReturn(ErrorDefs.ParameterInvalid).response

    date = parse(date)
    conn = instance.datasourceManager.get('mongodb').conn
    dbname = 'TradeFisher_{}-{}-{}'.format(date.year, date.month, date.day)
    db = conn[dbname]
    model.CodeSettings.__database__ = db
    model.CodePrice.__database__ = db
    model.CodePosition.__database__ = db
    result = []
    for cs in model.CodeSettings.find(strategy_id = strategy_id):
        data = cs.dict()
        price = model.CodePrice.get(code = cs.code)
        if price:
            data['price'] =  price.dict()
            data['price']['time'] = str(data['price']['time'])
        pos = model.CodePosition.get(strategy_id = strategy_id , code = cs.code)
        if pos:
            data['pos'] = pos.dict()
        result.append( data )
    return CR(result = result).response

"""
http://localhost:7788/fisher/api/strategy/code/logs?date=2019-5-15&strategy_id=AJ_ZF_InDay&code=002367

"""
def get_code_trade_logs():
    date = request.values.get('date', '')
    strategy_id = request.values.get('strategy_id')
    code = request.values.get('code')
    if not strategy_id or not date:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response
    date = parse(date)
    conn = instance.datasourceManager.get('mongodb').conn
    dbname = 'TradeFisher_{}-{}-{}'.format(date.year, date.month, date.day)
    db = conn[dbname]
    coll = db[strategy_id]
    rs = coll.find({'code':code}).sort('time',-1)
    result = []
    for r in list(rs):
        r['time'] = str(r['time'])
        del r['_id']
        result.append(r)
    return CR(result = result).response


import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
plt.switch_backend('agg')

title_font = FontProperties(family='YouYuan', size=18)
mpl.rcParams['axes.unicode_minus'] = False

def export_png_base64(fig):
    import StringIO
    import base64
    s = StringIO.StringIO()
    canvas=FigureCanvasAgg(fig)
    canvas.print_png(s)
    s.seek(0)
    data = "data:image/png;base64,"
    data += base64.encodestring(s.getvalue())
    s.close()
    return data


# http://192.168.99.21:7788/fisher/api/strategy/chart/boll?symbol=AP910
def get_array_chart_boll():
    """获取合约运行技术布林通道图"""
    from mantis.sg.fisher.stbase.futures import BarData
    from mantis.sg.fisher.stbase.array import ArrayManager

    product = request.values.get('product','futures') # 默认期货
    symbol = request.values.get('symbol')
    strategy_id = request.values.get('strategy_id')
    cycle = request.values.get('cycle',1,type=int)   # k线周期 ，默认 1分钟
    num = request.values.get('num',100,type=int)     # 策略选取的多少根k线
    lasttime = request.values.get('lasttime') # 查询最近截止的时间，默认为当前时间
    if lasttime:
        lasttime = parse(lasttime)
    else:
        lasttime = datetime.datetime.now()

    conn = instance.datasourceManager.get('mongodb').conn
    db = None
    if product == 'futures':
        name = 'Ctp_Bar_{}'.format(cycle)
        db = conn[name]
    coll = db[symbol]
    rs = coll.find({'datetime':{'$lte':lasttime} }).sort('datetime',-1).limit(num)
    rs = list(rs)
    rs.reverse()
    close = map(lambda _: _['close'],rs)
    date = map(lambda _: _['datetime'],rs)
    print close[-3:]
    if not close:
        return CR(result='').response
    am = ArrayManager().setCloseArray(close)
    up,down = am.boll(20,2,array=True)

    mid = am.ma(20, array=True)
    fig, ax = plt.subplots(figsize=(24,8))
    # fig, ax = plt.subplots()
    # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))
    ax.plot(date,up, label='up')
    ax.plot(date,down, label='down')
    ax.plot(date,mid, label='mid')
    ax.plot(date,close, marker='.',label='close')
    # ax.scatter(range(num),close,marker='.',label='close')
    ax.legend()
    ax.grid(True)
    # for index,_ in enumerate (close):
    #     x,y = date[index], close[index]
    #     t = ax.text( index,y, str(y), withdash=True)


    base64image = export_png_base64(fig)
    plt.cla()
    # ax.close()
    plt.close("all")
    return CR(result=base64image).response


# http://192.168.99.21:7788/fisher/api/strategy/ticks?symbol=AP910&lasttime=?&firsttime=?
def get_tick_chart():
    """获取指定时间范围的分时tick"""
    from mantis.sg.fisher.stbase.futures import BarData
    from mantis.sg.fisher.stbase.array import ArrayManager

    product = request.values.get('product','futures') # 默认期货
    symbol = request.values.get('symbol')
    strategy_id = request.values.get('strategy_id')
    # cycle = request.values.get('cycle',1,type=int)   # k线周期 ，默认 1分钟
    num = request.values.get('num',500,type=int)     # 策略选取的多少根k线
    lasttime = request.values.get('lasttime') # 查询最近截止的时间，默认为当前时间
    firsttime = request.values.get('firsttime') # 查询最近截止的时间，默认为当前时间
    if lasttime:
        lasttime = parse(lasttime)
    else:
        lasttime = datetime.datetime.now()

    if firsttime:
        firsttime = parse(firsttime)


    conn = instance.datasourceManager.get('mongodb').conn
    db = None
    if product == 'futures':
        name = 'Ctp_Tick'
        db = conn[name]
    coll = db[symbol]

    if not firsttime:
        firsttime = datetime.datetime(2010,1,1)
    rs = coll.find({'DateTime_':{'$lte':lasttime,'$gte':firsttime} }).sort('DateTime_',-1)

    if num:
        rs = rs.limit(num)
    rs = list(rs)
    p1 = rs[0]

    rs.reverse()
    p2 = rs[0]

    last = map(lambda _: _['LastPrice'],rs)
    ask = map(lambda _: _['AskPrice1'],rs)
    bid = map(lambda _: _['BidPrice1'],rs)
    date = map(lambda _: _['DateTime_'],rs)

    # am = ArrayManager().setCloseArray(close)
    # up,down = am.boll(20,2,array=True)
    #
    # mid = am.ma(20, array=True)
    fig, ax = plt.subplots(figsize=(24,8))
    # fig, ax = plt.subplots()
    # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))
    ax.plot(date,last, label='last')
    # ax.plot(date,ask, label='ask')
    # ax.plot(date,bid, label='bid')
    # ax.plot(date,close, marker='.',label='close')
    # ax.scatter(range(num),close,marker='.',label='close')
    ax.legend()
    ax.grid(True)
    # for index,_ in enumerate (close):
    #     x,y = date[index], close[index]
    #     t = ax.text( index,y, str(y), withdash=True)


    base64image = export_png_base64(fig)
    plt.cla()
    # ax.close()
    plt.close("all")
    return CR(result=base64image).response


def ctp_strategy_run():
    """加载运行策略"""
    start_time = current_datetime_string()
    mode = request.values.get('mode','test')
    strategy_id = request.values.get("strategy_id",'')
    st = model.StrategyParam.get(strategy_id = strategy_id)

    main = instance.serviceManager.get("main")
    locust_dir = main.getConfig().get('locust_home')
    path = os.path.join(locust_dir,'scripts/st-load.sh')
    params = st.run_test_params
    if mode == 'real':
        params = st.run_real_params

    cmd = 'bash {} {} {} {}'.format(path,st.script,st.strategy_id,params)
    print 'System Exec:',cmd
    os.system(cmd)

    return CR(result=start_time).response

def ctp_strategy_stop():
    """停止策略运行"""
    strategy_id = request.values.get("strategy_id", '')
    main = instance.serviceManager.get("main")
    locust_dir = main.getConfig().get('locust_home')
    path = os.path.join(locust_dir, 'scripts/st-stop.sh')

    cmd = 'bash {} {} '.format(path,strategy_id)
    print 'System Exec:', cmd
    os.system(cmd)
    return CR().response

def ctp_strategy_status_info():
    """返回策略运行状态信息
    - 包括当前是否在运行以及开始时间
    """
    # strategy_id = request.values.get("strategy_id", '')
    # st = model.StrategyParam.get(strategy_id = strategy_id)
    result = []
    for st in model.StrategyParam.find():
        st.running = False
        start = st.up_time
        if not start:
            start = parse('2000-1-1')

        distance = datetime.datetime.now() - start
        if distance.seconds <= 3:
            st.running = True

        st.start_time = datetime_to_str(st.start_time)
        st.up_time = datetime_to_str(st.up_time)
        result.append(st.dict())

    # main = instance.serviceManager.get("main")
    return CR(result= result).response

def ctp_strategy_code_status_info():
    """返回策略的合约代码运行参数信息"""
    strategy_id = request.values.get('strategy_id','')
    code = request.values.get('code')
    cs  = model.CodeSettings.get(strategy_id=strategy_id , code = code )

    return CR(result=cs.dict()).response

def ctp_strategy_log_delete():
    """删除指定时间段的日志"""
    strategy_id = request.values.get('strategy_id')
    code = request.values.get('code ')

def ctp_chart_wr_atr():
    strategy_id = request.values.get('strategy_id')
    code = request.values.get('code')
    rs = model.StrategyRunningView.collection().find( dict(strategy_id=strategy_id,code = code) ).sort('issue_time',-1).limit(1)
    result = {}
    if rs:
        r = rs[0]
        # del r['_id']
        # r['issue_time'] = datetime_to_str(r['issue_time'])
        result = normal_dict(r)
    return CR(result=result).response

def strategy_logs_last():
    strategy_id = request.values.get('strategy_id')
    start_time = request.values.get('start_time')
    start_time = parse(start_time)
    # messages = model.TradeMessageLog.collection().find({'strategy_id': strategy_id}).sort('issue_time', -1)

    # rs = model.TradeMessageLog.collection().find( {'issue_time':{'$gte',start_time}}).sort('issue_time',-1)
    rs = model.TradeMessageLog.collection().find( {'strategy_id': strategy_id,'issue_time':{'$gte':start_time}}).sort('issue_time',1)
    # rs = model.TradeMessageLog.collection().find( {'strategy_id': strategy_id}).sort('issue_time',1)

    # rs = model.TradeMessageLog.find(strategy_id=strategy_id)[:10]
    # rs = model.TradeMessageLog.collection().find( {'strategy_id': strategy_id})
    result = []
    for r in rs:
        text = 'code:{} title:{} message:{}'.format(r['code'],r['title'],r['message'])
        result.append(text)
    print '-*'*20
    print result
    return CR(result=result).response