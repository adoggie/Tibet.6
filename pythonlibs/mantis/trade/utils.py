# coding:utf-8

import time
import json
from mantis.trade.constants import ServiceKeepAlivedTime
from mantis.trade.constants import *
from vnpy.trader.vtObject import VtTickData,VtContractData,VtContractCommissionRateData,VtDepthMarketData

from mantis.trade.types import ProductClass

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import object_assign

def get_service_live_time(redis,service_name):
    """
    查询指定服务程序的运行存活时间
    :param service_name:
    :return:
    """
    return get_service_status(redis,service_name).get('live_time',0)

def get_service_status(redis,service_name):
    """查询服务的运行状态信息"""
    return redis.hgetall()


def is_service_alive(live_time):
    return time.time() - live_time < ServiceKeepAlivedTime

def get_contract_detail(symbol,type_=ProductClass.Future):
    conn = instance.datasourceManager.get('redis').conn
    text = ''
    try:
        if type_ == ProductClass.Future:
            text =  conn.hget(CTAContractListKey,symbol)
        elif type_ ==ProductClass.Stock:
            text = conn.hget(XtpContractListKey,symbol)
        dict_ = json.loads(text)

        contract = VtContractData()
        contract.__dict__ = dict_
    except :
        return None
    return contract

def get_depth_market_data(symbol):
    """查询合约深度行情数据"""
    conn = instance.datasourceManager.get('redis').conn
    text = ''
    data = None
    try:
        text = conn.hget(CtpDepthMarketDataListKey, symbol)
        dict_ = json.loads(text)
        data = VtDepthMarketData()
        data.__dict__ = dict_
    except:
        return None
    return data

def get_contract_commission_rate(symbol):
    """查询手续费率，注意: symbol是产品名称，不是合约全民，例如: m, IF ,.."""
    conn = instance.datasourceManager.get('redis').conn
    text = ''
    data = None
    product = get_symbol_prefix(symbol)
    try:
        text = conn.hget(CTAContractCommissionListKey, product)
        dict_ = json.loads(text)
        data = VtContractCommissionRateData()
        data.__dict__ = dict_
    except:
        return None
    return data

def get_trade_contract_data(symbol):
    """查询合约 相关的全部信息，包括：高低限价，手续费，开仓平仓费用等等
    """
    from mantis.trade.objects import TradeContractData
    contract = get_contract_detail(symbol)
    market = get_depth_market_data(symbol)

    commission = get_contract_commission_rate(symbol)
    data = None
    if contract and market and commission:
        data = TradeContractData()

        object_assign(data,market.__dict__)
        object_assign(data,commission.__dict__)
        object_assign(data, contract.__dict__)
    return data

def get_current_tick(symbol,type_=ProductClass.Future):
    """查询合约当前最新的价格"""
    redis = instance.datasourceManager.get('redis').conn
    key_name = ''
    try:
        if type_ == ProductClass.Future:
            key_name = CtpMarketSymbolTickFormat.format(symbol=symbol)
        elif type_ == ProductClass.Stock:
            key_name = XtpMarketSymbolTickFormat.format(symbol=symbol)
        data = redis.hgetall(key_name)

        tick = VtTickData()
        tick.__dict__ = data
    except:
        return None
    return tick

def get_symbol_prefix(symbol):
    import re
    m = re.findall('^([A-Za-z]{1,3})\d{2,5}', symbol)
    if m:
        return m[0].upper()
    return ''

def get_all_contracts(type_=ProductClass.Future):
    """获取所有合约信息"""
    conn = instance.datasourceManager.get('redis').conn
    text = ''
    result = {}
    try:
        many = {}
        if type_ == ProductClass.Future:
            many =  conn.hgetall(CTAContractListKey)
        elif type_ ==ProductClass.Stock:
            many = conn.hget(XtpContractListKey)

        for symbol,data in many.items():
            if not verify_contract_name(symbol):
                continue
            dict_ = json.loads(text)
            contract = VtContractData()
            contract.__dict__ = dict_
            result[symbol] = contract
    except Exception ,e:
        print 'Error: Read Contract Info :',str(e)
    return result

def verify_contract_name(name):
    """过滤合规的合约名称 ，不包含组合套利合约"""
    if name.count('-') or name.count('&') or len(name) > 8:
        # print 'Skip Contract:',name
        return None
    return name