#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object,object_assign
from bson import ObjectId
from mantis.BlueEarth.types import PositionSource,AlarmSourceType,CoordinateType

from mantis.fundamental.nosql import model
from mantis.fundamental.nosql.model import Model

# database = None

def get_database():
    service = instance.serviceManager.get('main')
    database = service.get_database()
    return database

"""
_id - mongodb object id 
id() - 获得 _id 的字符类型

"""
class __Model(object):
    def __init__(self):
        self._id = None
        self.__collection__ = self.__class__.__name__

    @property
    def id_(self):
        return str(self._id)

    @classmethod
    def find(cls,**kwargs):
        clsname = cls.__name__
        coll = get_database()[clsname]
        rs = coll.find(kwargs)
        result =[]
        for r in list(rs):
            obj = cls()
            object_assign(obj,r)
            result.append(obj)
        return result

    def dict(self):
        data = hash_object(self)
        if data.has_key('_id'):
            del data['_id']
        return data

    # @staticmethod
    # def get(self,**kwargs):
    #     pass

    @classmethod
    def collection(cls):
        coll = get_database()[cls.__name__]
        return coll

    @classmethod
    def get(cls,**kwargs):
        obj = cls()
        coll =  get_database()[cls.__name__]
        data = coll.find_one(kwargs)
        if data:
            object_assign(obj,data)
            return obj
        return None

    @classmethod
    def get_or_new(cls, **kwargs):
        obj = cls.get(**kwargs)
        if not obj:
            obj = cls()
            object_assign(obj,kwargs)
        return obj

    def assign(self,data):
        object_assign(self,data)

    def delete(self):
        """删除当前对象"""
        coll = get_database()[self.__collection__]
        coll.delete_one({'_id':self._id})

    def update(self,**kwargs):
        """执行部分更新"""
        coll = get_database()[self.__collection__]
        coll.update_one({'_id':self._id},update={'$set':kwargs},upsert = True)
        return self

    def save(self):
        coll = get_database()[self.__collection__]
        data = hash_object(self, excludes=['_id','id_'])
        if self._id:
            self.update(**data)
        else:
            self._id = coll.insert_one(data).inserted_id
        return self

    @classmethod
    def spawn(cls,data):
        """根据mongo查询的数据集合返回类实例"""

        # 单个对象
        if isinstance(data,dict):
            obj = cls()
            object_assign(obj,data)
            return obj
        # 集合
        rs = []
        for r in data:
            obj = cls()
            object_assign(obj, data)
            rs.append(obj)
        return rs

    @classmethod
    def create(cls,**kwargs):
        obj = cls()
        object_assign(obj,kwargs)
        return obj

    def __getattr__(self, name):
        return self.__dict__.get(name,None)
    
    def get_value(self,name,default=None):
        value = self.__dict__.get(name,None)
        if not value:
            value = default
        return value

class InnerBox(Model):
    """室内机记录清单"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.sn = ''            # 设备编号
        self.os = ''            # 系统类型
        self.mac = ''           # mac 地址
        self.ip = ''            # ip地址
        self.room_id = ''       # 房号
        self.sign_key = ''      # 数据签名秘钥
        self.login_time  = 0   # 设备登录时间
        self.access_token = ''  # 访问令牌
        self.token = ''         # 登录令牌
        self.ver = ''  # 版本
        self.family_ip = ''     # 室内接口地址
        self.family_call_port = 0   # 室内呼叫端口
        self.garden_id = ''     # 园区编号
        self.building_id = ''   # 单元楼编号


class InnerScreen(Model):
    """室内屏记录清单"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.sn = ''  # 设备编号
        self.os = ''  # 系统类型
        self.mac = ''  # mac 地址
        self.ip = ''  # ip地址
        self.room_id = ''  # 房号
        self.sign_key = ''  # 数据签名秘钥
        self.login_time = 0  # 设备登录时间
        # self.access_token = ''  # 访问令牌
        self.token = ''  # 登录令牌
        self.ver = ''  # 版本
        self.family_ip = ''
        self.family_call_port = 0
        self.garden_id = ''  # 园区编号
        self.building_id = ''  # 单元楼编号

class OuterBox(Model):
    """室外机记录清单"""
    def __init__(self):
        Model.__init__(self)
        self.sn = ''  # 设备编号
        self.os = ''  # 系统类型
        self.mac = ''  # mac 地址
        self.ip = ''  # ip地址
        self.name = ''      # 室外机的名称 ( 1楼，负1楼）
        self.sign_key = ''  # 数据签名秘钥
        self.login_time = 0  # 设备登录时间
        self.token = ''     # 登录令牌
        self.type = 'B'      # A: 围墙机 , B: 单元机
        self.floor = 1      # -1： 地下一层 , 1:地上一层
        self.is_primary = 1      # 是否为室内机访问的主室外机 0 : 否 , 1- 是
        self.ver = ''       # 版本
        self.garden_id = ''  # 园区编号
        self.building_id = '' # 单元楼编号


class PropertyCallApp(Model):
    """物业呼叫App端"""
    def __init__(self):
        Model.__init__(self)
        self.sn = ''  # 设备编号
        self.os = ''  # 系统类型
        self.mac = ''  # mac 地址
        self.ip = ''  # ip地址
        self.port  = 0  # 端口
        self.name = ''  # 室外机的单元编码
        self.sign_key = ''  # 数据签名秘钥
        self.login_time = 0  # 设备登录时间
        self.token = ''  # 登录令牌
        self.ver = ''  # 版本
        self.garden_id = ''    # 园区编号


class SentryApp(PropertyCallApp):
    """岗亭机App端"""
    def __init__(self):
        PropertyCallApp.__init__(self)

class CallHistory(Model):
    def __init__(self):
        Model.__init__(self)
        self.src_name = ''        # 设备名称 (房间号码、单元机名称)
        self.dest_name = ''
        self.src_id = ''        # 主叫设备编号
        self.dest_id = ''          # 被叫设备编号
        self.start_time = 0     # 呼叫时间
        self.end_time = 0     # 呼叫时间
        self.src_type = 0     # 主叫类型    1: 室内主机 ，2：室内屏设备 ，3：室外机 ， 4： 物业App; 5:其他
        self.dest_type = 0
        self.src_ip = ''   # 设备ip
        self.dest_ip = ''     #


class DeviceBaseLog(Model):
    """设备运行基础日志"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.id=  ''    # 设备编号
        self.os = ''
        self.ver = ''  # 版本
        self.ip = ''
        self.time = None        # 设备时间
        self.event = ''     #时间内类型
        self.sys_time = None     # 系统时间
        self.content = ''


class InnerScreenLog(DeviceBaseLog):
    """室内屏日志"""
    def __init__(self):
        DeviceBaseLog.__init__(self)
        self.name = ''
        self.room_id = ''
        
class InnerBoxLog(DeviceBaseLog):
    """室内屏日志"""
    def __init__(self):
        DeviceBaseLog.__init__(self)
        self.room_id = ''

class OuterBoxLog(DeviceBaseLog):
    """室外机日志"""
    def __init__(self):
        DeviceBaseLog.__init__(self)

class PropertyAppLog(DeviceBaseLog):
    """物业App日志"""
    def __init__(self):
        DeviceBaseLog.__init__(self)

class SentryAppLog(DeviceBaseLog):
    """岗亭机App日志"""
    def __init__(self):
        DeviceBaseLog.__init__(self)

class DeviceBaseStatus(Model):
    """设备运行状态"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''
        self.type = 0   # 设备类型
        self.id=  ''    # 设备编号
        self.os = ''
        self.ver = ''  # 版本
        self.ip = ''
        self.time = None        # 设备时间
        # self.event = ''     #时间内类型
        self.sys_time = None     # 系统时间
        self.detail = ''

class HomeGarden(Model):
    """园区信息"""
    def __init__(self):
        Model.__init__(self)
        self.name = 'master'  # 名称
        self.id = '8888'    # 编号

        self.property_server_url = '' # 物业服务器地址
        self.stream_server_url = ''
        self.property_call_server = ''        # 呼叫服务器地址

class Building(Model):
    """单元楼"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''  # 单元楼名称
        self.id = ''    # 编号


class Emergency(Model):
    """报警触发和处理记录"""
    def __init__(self):
        Model.__init__(self)
        self.room_id = ''   # 房号
        self.type = ''      # 报警类型
        self.time = None    #
        self.sys_time = None
        self.port = 0
        self.name = ''
        self.detail = ''
        self.secret_key = ''    # 报警时生成的安全秘钥用于下发控制

        self.confirm_time = None # 确认时间
        self.confirm_operator = ''  # 确认人
        self.confirm_ip = ''        # 确认登录ip
        self.confirm_message = ''   # 确认信息

class UpgradeConfig(Model):
    """登记设备需要进行升级信息"""
    def __init__(self):
        Model.__init__(self)
        self.version = ''   # 需更新到的版本
        self.media_url = '' # 更新的软件压缩包地址
        self.md5 = ''       # 校验值
        self.enable = 0     # 是否启用
        self.type = 0       #  1: 室内主机 ，2：室内屏设备 ，3：室外机 ， 4： 物业App; 5:其他
        self.ip = ''        # 指定需要升级的ip地址相关的设备


class PropertyServerLog(Model):
    """物业服务器日志"""
    def __init__(self):
        Model.__init__(self)
        self.sys_time = None
        self.event = ''     # 业主房间报警开门
        self.detail = ''

# 以下代碼必須保持，在每一個模塊的model中必須複製,以便於支持 Model在不同的數據庫中
var_locals = locals()

def set_database(database):
    model.set_database(var_locals,database)
