#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object,object_assign
from bson import ObjectId
from mantis.BlueEarth.types import PositionSource,AlarmSourceType,CoordinateType

# database = None

def get_database():
    service = instance.serviceManager.get('main')
    database = service.get_database()
    return database



class Model(object):
    def __init__(self):
        self._id = None
        self.__collection__ = self.__class__.__name__

    @property
    def id(self):
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
        data = hash_object(self, excludes=['_id'])
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


class HostDevice(Model):
    """设备信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''     # 设备唯一编号
        self.device_type = ''   # 设备类型 gt310,..
        self.name = ''          # 设备名称
        self.vendor = ''
        self.imei =''
        self.sim =''
        self.mobile = ''        # 移动电话 需要人工输入
        self.password = ''      # 设备管理密码
        self.salt = ''
        self.admin_mobile = ''  # 管理手机号，用于密码找回
        self.active = False     # 是否激活启用
        self.active_time = 0    # 开通时间
        self.expire_time = 0    # 过期时间
        self.update_time = 0    # 更新时间
        self.update_user = ''   # 更新的用户
        self.short_id = ''      # 设备短码

class EndpointDevice(Model):
    """终端设备"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''         # 终端设备id
        self.host_device_id = ''    # 主机设备编号
        self.active_time = 0        # 上线时间
        self.device_type = ''       # 设备类型


class HostDeviceStatus(Model):
    """终端设备运行日志"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''
        self.update_time = 0  # 上报时间
        

class EndpointDeviceStatus(Model):
    """终端设备运行日志"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''
        self.host_device_id = ''  # 主机设备编号
        self.update_time = 0  # 上报时间


class EndpointDeviceCommandSent(Model):
    """终端设备的命令发送记录"""
    def __init__(self):
        Model.__init__(self)
        self.device_id  =''
        self.issue_time = 0
        self.sender = ''        # 命令发送者
        self.sender_type = ''   # 发送者类型
        self.content = ''          # 发送内容

class User(Model):
    def __init__(self):
        Model.__init__(self)
        self.account = ''       # 账户名
        self.password = ''      # 登录密码
        self.salt = ''          # 随机数
        self.user_type = ''     # admin,user
        self.name   = ''        # 用户名称
        self.wx_user  = ''      # 微信账号
        self.platform = ''      # wx,mobile
        self.avatar   = ''      # 头像
        self.mobile     = ''    # 移动电话
        self.last_login = 0     # 登录时间
        self.expire_time = 0    # 过期时间
        self.update_time = 0    # 更新时间
        self.token = ''
        self.email = ''
        self.address = ''


class Group(Model):
    """设备组，可进行分级，父子管理"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''          # 组名称
        self.comment = ''       # 说明
        self.order = 0          # 排序
        self.parent = 0         # 父节点
        self.path = ''          # 组结构位置 a-b-c
        self.user_id = ''       # 隶属于用户
        self.create_time = 0    # 创建时间
        self.update_time = 0    # 更新时间

class DeviceGroupRelation(Model):
    """组合设备关系 , N对N关系"""
    def __init__(self):
        Model.__init__(self)
        self.group_id = ''   # 组编号
        self.device_id = ''  # 设备编号
        self.update_time = 0    # 更新时间
        self.user_id = ''    # 记录用户id , 冗余
        self.order = 0      # 排序
        

class DeviceUserRelation(Model):
    """设备与用户关系 ( N - N )"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''       # 用户编号
        self.device_id = ''     # 设备记录编号
        self.device_name = ''   # 设备名称
        self.device_image = ''  # 设备图片
        self.device_type =''

        self.update_time = 0    # 更新时间
        self.is_share_device = False  # 是否是分享设备
        self.share_user_id = ''     # 分享设备的用户编号 冗余
        self.share_device_link  = ''   # 如果是他人分享
        self.order = 0   # 排序，置顶项采用当前  时间戳*-1
        self.map_scale = 16  # 地图当前缩放比

class CommandSend(Model):
    """设备在线命令发送记录"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''         # 设备编号
        self.send_time = 0          # 发送时间
        self.sequence = 1           # 系统流水号
        self.ack_time = 0           # 回应时间
        self.command = ''           # 命令名称
        self.content = ''           # 命令参数

class  DeviceConfig(Model):
    """设备运行配置参数"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''         # 设备编号
        self.device_type = ''       # gt310
        self.imei = ''              # 硬件编码
        self.sim = ''               # sim卡号
        self.ver = ''
        self.sos_1 = ''
        self.sos_2 = ''
        self.sos_3 = ''
        self.sos_4 = ''
        self.server_mode ='ip'      # ip or domain
        self.server_ip=''
        self.server_domain=''
        self.server_port = 25002
        self.pos_mode = 'smart'       # 定位模式 timing:定时 , start:智能
        self.gps_timer = 0            # 上传频率 s
        self.lbs_timer = 0            # lbs 上传描述
        self.heartbeat_timer = 0      # 心跳间隔
        self.battery_alarm_enable = 0 # 电池报警
        self.shake_alarm_enable  = 0   # 震动报警
        self.sos_alarm_enable = 0   #
        self.fence_alarm_enable = 0 # 围栏报警是否启用
        self.gps_enable = 1     # 启用gps定位
        self.lbs_enable = 1     # 启用lbs
        self.wifi_enable = 1    # 启用wifi ， 用于在定位和轨迹时是否忽略相关的记录
        self.pos_timer = 30     # 定位时间频率
        self.fly_enable = 1     #
        self.fly_timespan= '22:00-07:00'      # 22:00-07:00



class Feedback(Model):
    """用户反馈问题"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''
        self.open_id = ''
        self.create_time = 0
        self.title =''      # 问题主题
        self.content=''     # 问题内容
        self.reply = ''     # 回复内容
        self.replier = ''   # 回复人
        self.reply_time = 0 # 回复时间


class LogLogin(Model):
    """用户登录日志"""
    def __init__(self):
        Model.__init__(self)
        self.account = ''  # 登录账户名称
        self.open_id = ''  # weixin
        self.platform = ''  # 平台
        self.datetime = ''  #
        self.timestamp = 0  #
        self.succ = False   # 登录
        self.reason = ''    # 错误原因
        self.remote_ip = ''

class LogSms(Model):
    """短信发送日志"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''
        self.open_id = ''   # 用户id
        self.datetime = ''  #
        self.timestamp = 0  #
        self.phones = ''  # 目标电话
        self.req_id = ''    # 请求号
        self.biz_id = ''    # 业务号（返回)
        self.sign = ''      # 短信签名
        self.template = ''  # 短信模板代码
        self.content = ''   # 短信内容
        self.succ = False    # 是否成功
        self.reason = ''    #  find_password

from mantis.fundamental.nosql.mongo import Connection
if __name__ == '__main__':
    conn = Connection().conn
    coll = conn['TradeLog_Ctp_htqh-01']['send_order']
    rs = coll.find()
    for r in rs :
        print r
    # print type(rs)