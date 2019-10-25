#coding:utf-8

import json
import datetime
import traceback

from flask import Flask,send_file
from flask import Response

from flask import render_template , request,redirect,url_for

import  requests

from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.utils import nocache
from mantis.fundamental.utils.useful import object_assign
from mantis.sg.fisher.model import model
from mantis.sg.fisher.stbase.futures import Position,OrderRecord,TradeReturn
from mantis.fundamental.utils.mongo import normal_dict
# http://192.168.99.21:7788/console/charts/boll?symbol=AP910

@nocache
def chart_boll():
    symbol = request.values.get('symbol')
    return render_template('charts.html',symbol=symbol)

def orders():
    main = instance.serviceManager.get('main')
    controller = main.controller

    http = instance.serviceManager.get('http')
    http = http.cfgs.get('http')
    host = http.get('host')
    port = http.get('port')
    url = "http://{}:{}/api".format(host,port)
    accounts =[]
    for account in controller.futureHandler.accounts.values():
        accounts.append( {'product':account.product,'account':account.account})
    return render_template('orders.html', http_url = url, accounts=accounts)


@nocache
def main():
    return render_template('ctp-main.html')

# api_server_url =

@nocache
def conn_list():
    conns = model.ConnectionUrl.find()
    for conn in conns:
        strategies = []
        for _ in model.StrategyParam.find(conn_url=conn.id):
            s = dict(status=u'未启动',start_time='',up_time='')
            if _.start_time:
                s['status'] = u'已启动'
                s['start_time'] = str(_.start_time)
            if _.up_time:
                s['up_time'] = str(_.up_time)
            s['strategy_id'] = _.strategy_id
            s['comment'] = _.comment


            code_list = []
            for cs in model.CodeSettings.find(strategy_id = _.strategy_id):
                data = dict(code=cs.code,name=cs.name)
                code_list.append(data)
            s['code_list'] = code_list

            strategies.append(s)

        conn.strategies = strategies


    return render_template('ctp-conn-list.html',conns = conns)


# 显示行情
@nocache
def hq_list():
    subscribed_symbols = '' # 订阅的合约名称列表
    main = instance.serviceManager.get('main')
    server_url = main.getConfig().get('latchet_server')
    quotes_server =  "{}/quotes".format(server_url) # 行情实时分发服务地址
    cs_list = model.CodeSettings.find()
    codes = []
    subscribed_symbols = []
    for cs in cs_list:
        codes.append(dict(code=cs.code,exchange=cs.exchange_id))
        subscribed_symbols.append(cs.code)

    # codes = instance.serviceManager.get("main").getConfig().get("subscribed_symbols",'').split(',')
    subscribed_symbols = ','.join(subscribed_symbols)
    return render_template('ctp-hq-list.html',codes=codes,subscribed_symbols=subscribed_symbols,quotes_server=quotes_server)


def query_resp_funds(conn_id):
    """资金返回"""
    conn = model.ConnectionUrl.get(id = conn_id)
    url = conn.td_api_url + '/ctp/account'
    res = requests.get(url,timeout=3)
    data = res.json().get('result', {})
    return data

@nocache
def account_info():
    conn_id = request.values.get('id')
    funds = query_resp_funds(conn_id)

    strategies = model.StrategyParam.find()

    return render_template('ctp-account-info.html', funds=funds , conn_id = conn_id)


def getPosition(conn_id):
    """查询指定 代码或者指定策略的持仓记录"""
    conn = model.ConnectionUrl.get(id=conn_id)
    url = conn.td_api_url + '/ctp/position/list'
    result = []
    try:
        res = requests.get(url,timeout=3)
        values = res.json().get('result', [])
        for _ in values:
            if not _.get('InstrumentID'):
                continue
            pos = Position()
            object_assign(pos, _)
            result.append(pos)
    except:
        traceback.print_exc()
    return result

@nocache
def position_list():
    conn_id = request.values.get('id')
    positions = getPosition(conn_id)

    return render_template('ctp-position-list.html', positions=positions , conn_id = conn_id)


def getOrders(conn_id):
    """查询委托信息，状态包括： 未成、部分成、全成、错误
        strategy_id 作为 委托的 orign source  字段
    """
    conn = model.ConnectionUrl.get(id=conn_id)
    url = conn.td_api_url + '/ctp/order/list'

    orders = []
    try:
        res = requests.get(url,timeout=3)
        values = res.json().get('result',[])

        for _ in values:
            if not _.get('InstrumentID'):
                continue
            order = OrderRecord()
            object_assign(order,_)
            order.normalize()
            orders.append(order)
    except:
        traceback.print_exc()
    return orders

@nocache
def order_list():
    conn_id = request.values.get('id')
    orders = getOrders(conn_id)
    orders.reverse()
    return render_template('ctp-order-list.html', orders=orders , conn_id = conn_id)


def getTradeRecords(conn_id):
    conn = model.ConnectionUrl.get(id=conn_id)
    url = conn.td_api_url + '/ctp/trade/list'

    result = []
    try:
        res = requests.get(url,timeout=3)
        values = res.json().get('result',[])

        for _ in values:
            tr = TradeReturn()
            object_assign(tr,_)
            tr.normalize()

            result.append(tr)
    except:
        traceback.print_exc()
    return result

@nocache
def trade_list():
    conn_id = request.values.get('id')
    trades = getTradeRecords(conn_id)

    return render_template('ctp-traded-list.html', trades=trades , conn_id = conn_id)

#策略交易信号
@nocache
def strategy_logs_order():
    sid = request.values.get('strategy_id')
    orders = model.TradeOrder.collection().find({'strategy_id': sid}).sort('issue_time', -1).limit(100)

    return render_template('ctp-strategy-logs-orders.html', orders=orders , strategy_id = sid)

# 策略运行消息
@nocache
def strategy_logs_message():
    main = instance.serviceManager.get('main')
    server_url = main.getConfig().get('latchet_server')
    log_server = "{}/strategy-logs-message".format(server_url)  # 行情实时分发服务地址
    sid = request.values.get('strategy_id')
    messages = model.TradeMessageLog.collection().find({'strategy_id':sid}).sort('issue_time',-1).limit(100)
    return render_template('ctp-strategy-logs-message.html', strategy_id=sid, messages = messages ,log_server= log_server)


@nocache
def strategy_code_status():
    """显示代码运行状态参数"""
    sid = request.values.get('strategy_id')
    code = request.values.get('code')
    cs = model.CodeSettings.get(strategy_id = sid, code = code )
    values = []
    for k,v in cs.dict().items():
        if k.startswith('sub_') or k.startswith('_'):
            continue
        if k in ('id_','strategy_id','code','name'):
            continue
        values.append(dict(name=k,value=v))
    values = sorted(values,cmp= lambda x,y:cmp(x['name'],y['name']) )
    return render_template('ctp-strategy-code-status.html', cs = values,strategy_id=sid,code=code)

@nocache
def strategy_code_param_reset():
    sid = request.values.get('strategy_id')
    code = request.values.get('code')
    cs = model.CodeSettings.get(strategy_id=sid, code=code)
    cs_back = model.CodeSettingsInited.get(strategy_id=sid, code=code)
    cs.assign(cs_back.dict())
    cs.save()


    url ="/ctp/strategy/code/status" #?strategy_id={}&code={}".format(sid,code)
    return redirect(url_for('.strategy_code_status',strategy_id=sid,code=code))

@nocache
def strategy_charts():
    code = request.values.get('code')
    strategy_id = request.values.get('strategy_id')
    now = datetime.datetime.now()
    date = '{}-{:02d}-{:02d}'.format(now.year,now.month,now.day)
    return render_template('ctp-strategy-code-running-chart.html',code=code,strategy_id=strategy_id, datetime = date)

@nocache
def get_bar_list():
    code = request.values.get('code')
    num = request.values.get('num',100,type=int)
    cycle = request.values.get('cycle','d')
    conn = instance.datasourceManager.get('mongodb').conn
    db = conn['Ctp_Bar_{}'.format(cycle)]
    coll = db[code]
    rs = coll.find({}).sort('time',-1).limit(num)
    bars = list(rs)
    return render_template('ctp-bar-list.html',bars = bars,code=code,cycle=cycle)

@nocache
def event_list():
    conn_url = request.values.get('conn_url')
    limit = request.values.get('limit',200,type=int)
    # rs = model.StrategyErrorLog.collection().find( dict(conn_url=conn_url) ).sort('issue_time',-1)[:limit]
    rs = model.StrategyErrorLog.collection().find().sort('issue_time',-1).limit(limit)
    # rs = model.CodeSettings.find()
    result =[]
    for r in rs:
        # result.append( r )
        result.append( normal_dict(r) )
    return render_template('ctp-trade-event-list.html',conn_url= conn_url,events = result)
