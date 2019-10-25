# coding:utf-8

import json
import datetime
from mantis.fundamental.application.app import instance
from vnpy.trader.vtObject import VtTickData

def get_device_message(message,ctx):
    """订阅的所有合约行情数据"""
    topic = ctx.get('name')     # 通道名称
    data = message
    device_id = topic.split('.')[-1]    # 最后一项为设备编号  DeviceChannelPub = 'blue_earth.device.channel.pub.{device_id}'
    message = json.loads(data)
    table = instance.getProp('SubscribeTable')
    if table:
        ns_name = ctx['channel'].cfgs.get('data',{}).get('ns_name')
        table.emit_message(ns_name,device_id,message)

