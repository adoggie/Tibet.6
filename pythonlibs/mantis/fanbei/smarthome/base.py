#coding:utf-8

import json


class Constants(object):
    Undefined = 0
    InvalidSensorId = Undefined

class ModuleType(object):
    Undefined = 0

    Major = 'host'   # 主机设备
    Minor = 'mcu'   # MCU控制器

    Primary = Major
    Secondary = Minor # sensor hub
    First = Major
    Second = Minor
    All = 3

class SensorType(object):
    """传感器模块类型"""
    Undefined = 0

    Relay = 1
    AirCondition = 2  # 空调
    All = 99

class SensorFeatureType(object):
    """传感器功能"""
    Undefined = ''
    Power = 'POW'       # 开关
    FanSpeed = 'FSD'    # 风速
    Temperature = 'TMP' # 温度
    Humidity = 'HUM'    # 湿度




class DeviceStatus(object):
    def __init__(self):
        self.id = ''    # 设备编号
        self.type = ''  # 主机类型
        self.version = ''       # 版本
        self.time = 0


