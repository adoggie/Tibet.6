#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object,object_assign
from bson import ObjectId

from mantis.fundamental.nosql import model
from mantis.fundamental.nosql.model import Model

# database = None

# def get_database():
#     service = instance.serviceManager.get('main')
#     database = service.get_database()
#     return database


class HomeProject(Model):
    """工程项目"""
    def __init__(self):
        Model.__init__(self)
        self.id = ''
        self.name = ''
        self.address = ''
        self.tel = ''
        self.desc = ''


class HomeGarden(Model):
    """园区"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.project_id = ''


class Building(Model):
    """楼宇"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.garden_id = ''
        self.project_id = ''


class BuildingUnit(Model):
    """单元楼"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.garden_id = ''
        self.building_id = ''
        self.project_id = ''


class Room(Model):
    def __init__(self):
        Model.__init__(self)
        self.id = ''
        self.name = ''
        self.building_id = ''
        self.template_id = ''       # 房型模板
        self.garden_id = ''
        self.project_id = ''
        self.device_id = ''         # 主控设备编号


class RoomTemplate(Model):
    """房型"""
    def __init__(self):
        Model.__init__(self)
        self.id = ''
        self.name = ''
        self.device_type = ''
        self.project_id = ''
        self.garden_id = ''
        self.profile = ''  # 设备现场的profile定义


class RoomArea(Model):
    """房屋区域"""
    def __init__(self):
        Model.__init__(self)
        self.id = ''
        self.name = ''          # 区域名称
        self.template_id = ''   # 房型类型编号
        # self.room_id = ''       # 房屋记录编号
        self.project_id = ''
        self.garden_id = ''


class DeviceServer(Model):
    """设备接入服务器信息"""
    def __init__(self):
        Model.__init__(self)
        self.id = ''          # 标识
        self.ip = ''        # ip地址
        self.port = 0         # 端口
        self.redis_queue = ''


class SmartDevice(Model):
    """主设备 arm 主机"""
    def __init__(self):
        Model.__init__(self)
        self.id = ''            # 设备唯一编号
        self.type = ''          # 设备类型
        self.name = ''          # 设备名称
        self.vendor = ''        # 厂商标识
        self.secret_key = ''    # 数据加密

        self.alive_time = ''    # 最近活跃时间
        self.status = 0         # 0 不可用 , 1 可用
        self.active_time = 0    # 激活时间
        self.server_id = ''     # 接入服务器编号(设备挂接在不同服务器)
        self.template_id = ''

        self.host_ver = ''  # 版本
        self.mcu_ver = ''
        self.status_time = 0  # 主机时间
        self.boot_time = 0  # 设备启动时间
        self.profile = ''



class Sensor(Model):
    """传感器模块"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''  # 设备名称
        self.id = 0      # 设备编号
        self.type = ''      # 传感器类型  灯光、温度,...
        self.area_id = ''           # 房间区域编号
        self.device_id = ''
        self.params = ''    # json


class LogDeviceStatus(Model):
    """设备状态信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''
        self.device_type = ''     # 设备编号
        self.host_ver = ''  # 版本
        self.mcu_ver = ''
        self.status_time = 0  # 主机时间
        self.boot_time = 0  # 设备启动时间
        self.sys_time = 0       # 系统时间
        # 这里包含多个运行值，包括 mcu 和 arm 两部分参数，例如： 当前 模式等等


# class LogSensorStatusSnapShot(Model):
#     """设备快照"""
#     def __init__(self):
#         Model.__init__(self)
#         self.device_id = ''  # 设备编号
#         self.sys_time = 0  # 服务器时间
#         self.sensor_id = ''  # 传感器编号
#         self.sensor_type = ''  # 传感器类型
#         self.room_id = ''  # 房间记录编号
#         self.area_id = ''  # 房间区域编号
#         # 以下多个运行参数
#         # ... param_xxx  添加 'param_' 前缀


class LogSensorStatus(Model):
    """传感器模块运行状态信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''     # 设备编号
        self.sys_time = 0       # 服务器时间
        self.sensor_id = ''     # 传感器编号
        self.sensor_type = ''   # 传感器类型
        self.room_id = ''       # 房间记录编号
        self.area_id = ''       # 房间区域编号
        self.datetime = None
        # self.param_name = ''    # 参数名
        # self.param_value = ''   # 参数值


class LogDeviceValueSet(Model):
    """传感器模块控制日志信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''     #
        self.sys_time = 0
        self.param_name = ''
        self.param_value = ''


class LogSensorValueSet(Model):
    """传感器模块控制日志信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''     #
        self.sensor_id = ''
        self.sensor_type = ''
        self.sys_time = 0
        self.param_name = ''
        self.param_value = ''


class LogDeviceLogInfo(Model):
    """传感器模块控制日志信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''
        self.sys_time = 0
        self.device_time = 0
        self.content = ''       # 日志信息


# 以下代碼必須保持，在每一個模塊的model中必須複製,以便於支持 Model在不同的數據庫中
var_locals = locals()


def set_database(database):
    model.set_database(var_locals,database)