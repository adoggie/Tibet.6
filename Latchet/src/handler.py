# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance

def get_ctp_symbol_ticks(message,ctx):
    """订阅的所有合约行情数据"""
    topic = ctx.get('name')
    data = message
    # topic: 订阅的通道名称 ctp_ticks_*
    symbol = topic.split('_')[-1]

    tick = json.loads(data)
    sub_table = instance.getProp('SubscribeTable')
    if sub_table:
        ns_name = ctx['channel'].cfgs.get('data',{}).get('ns_name')
        sub_table.emit_message(ns_name,symbol,tick)

    # def onTick(self, symbol, tickobj):
    #     try:
    #         data = tickobj.__dict__
    #         del data['datetime']
    #         self.emit_message(symbol, data)
    #         # self.broadcast_event('data',symbol,data)
    #     except:
    #         traceback.print_exc()

    """
    貌似凭借多年经验感觉错误在于 redis的接收线程读取数据之后，处理数据，并再将数据发送回redis，期间在一个线程中执行导致的故障 
    所以应该将接收的数据置入 Queue，处理程序从Queue中获取数据处理，并将数据发送回去 
    
    gevent能运行，但出现了故障，一个条件被重入了，所以肯定是这个问题
    """

def get_ctp_strategy_logs(message,ctx):
    """订阅的所有合约行情数据"""
    topic = ctx.get('name')
    data = message
    # topic: 订阅的通道名称 ctp_ticks_*
    symbol = topic.split('$')[-1]

    tick = json.loads(data)
    sub_table = instance.getProp('SubscribeTable')
    if sub_table:
        ns_name = ctx['channel'].cfgs.get('data',{}).get('ns_name')
        sub_table.emit_message(ns_name,symbol,tick)