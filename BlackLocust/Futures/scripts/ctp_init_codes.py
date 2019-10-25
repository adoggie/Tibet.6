#coding:utf-8
"""
初始化策略运行控制参数
"""
import  sys
import copy
import traceback
import time
import datetime
from dateutil.parser import parse
import requests
import copy

from mantis.sg.fisher.utils.useful import hash_object,object_assign
from mantis.sg.fisher import stbase
from mantis.sg.fisher import model as model
import config
from ctp_init_data import *

td_api_url = config.TRADE_API_URL

CODE_CLEARS = True

def init_mongodb(host='127.0.0.1',port=27017,date = None):
    """
    date : str 默认为当日
    """
    from pymongo import MongoClient
    dbname = config.STRATEGY_DB_NAME
    mg_conn = MongoClient(host, port)
    model.set_database(mg_conn[dbname])
    return mg_conn

def init_all():
    model.StrategyParam.collection().remove()

    model.CodeSettingsParamType.collection().remove()

    if CODE_CLEARS:
        model.CodeSettings.collection().remove()
    strategies_kvs = {}
    for _ in strategies:
        # strategies_kvs[_['strategy_id']] = copy.deepcopy( _ )
        strategies_kvs[_['strategy_id']] = _

        _ = copy.deepcopy(_)
        del _['codes']
        sp = model.StrategyParam()
        sp.assign(_)
        sp.save()

    for _ in strategies:
        codes = _['codes']

        # 初始化交易商品的参数信息
        # for code,params in codes.items():
        for item in codes:
            code = item['name']
            params = item

            cs = model.CodeSettings.get(code = code , strategy_id = _['strategy_id'])
            if params.get('clone_from'):
                its = params.get('clone_from','').split('/')
                sid = _['strategy_id']
                cd = ''
                if len(its) ==  1: # 赋值本strategy中的其他code参数
                    cd = its[0]

                if len(its) > 1:
                    sid,cd = its

                strategy = strategies_kvs[sid]

                codes_dict = {}
                for c in strategy['codes']:
                    codes_dict[c['name']] = c
                ps = codes_dict[cd]
                ps = copy.deepcopy(ps)
                ps.update(params) # 复制，并更新
                params.update( ps )
                # codes[code] = params

            # 是否覆写
            if cs:
                if CODES[code].get('_renew'):
                    cs.delete()
                    cs = None
            if not cs:
                cs = model.CodeSettings()
                cs.code = code
                # cs.name = CODES[code]
                cs.name = CODES[code].get('name')
                cs.exchange_id = CODES[code].get('exchange')
                cs.strategy_id = _['strategy_id']
                cs.assign( params ).save()

                cs_back = model.CodeSettingsInited()
                cs_back.assign(cs.dict())
                cs_back.save()

            for name,val in params.items():

                # code_params = hash_object(cs,excludes=('strategy_id','code','name'))
                cspt = model.CodeSettingsParamType()
                cspt.strategy_id = cs.strategy_id
                cspt.code = cs.code
                cspt.name = name
                cspt.conn_url = _['conn_url']
                p = val
                if isinstance(p,int):
                    cspt.type = 'int'
                elif isinstance(p,float):
                    cspt.type = 'float'
                elif isinstance(p,datetime.datetime):
                    cspt.type = 'datetime'
                elif isinstance(p,bool):
                    cspt.type = 'bool'
                else:
                    cspt.type = 'str'
                cspt.save()




def requestFreshInstrument(code):
    """请求trader 刷新合约信息"""
    print 'requestFreshInstrument() , code:',code
    url = td_api_url + '/ctp/instrument/query'
    data = {}
    try:
        params = dict(instrument=code)
        res = requests.post(url, params)
        data = res.json().get('result', {})
    except:
        traceback.print_exc()
    return data

def init_code_more_info():
    """初始化合约相关信息(手续费，保证金) ，写入响应的表中"""
    for code in CODES.keys():
        requestFreshInstrument(code)
        time.sleep(1)

    for code in CODES.keys():
        url = td_api_url + '/ctp/instrument/detail'
        data = {}
        try:
            params = dict(instrument=code)
            res = requests.get(url, params)
            data = res.json().get('result', {})
            item = model.CodeBasicInfo.get(code= code)
            if item:
                item.delete()

            item = model.CodeCommissionRate.get(code=code)
            if item:
                item.delete()

            item = model.CodeMarginRate.get(code=code)
            if item:
                item.delete()

            item = model.CodeBasicInfo()
            item.code = code
            item.name = data['instrument']['InstrumentName']
            item.assign(data['instrument'])
            item.save()

            item = model.CodeCommissionRate()
            item.code = code
            item.name = code
            item.assign(data['commission_rate'])
            item.save()

            item = model.CodeMarginRate()
            item.code = code
            item.name = code
            item.assign(data['margin_rate'])
            item.save()

        except:
            traceback.print_exc()


# 生成当天数据库的策略配置参数
if __name__ == '__main__':
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[-1]
    db = init_mongodb(host= config.STRATEGY_SERVER[0], port=config.STRATEGY_SERVER[1], date=date)

    init_all()
    # init_code_more_info()

    print 'Strategy Configuration Finished!'
    # print model.ConnectionUrl.get()


