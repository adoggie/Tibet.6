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


class Device(Model):
    """设备信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''     # 设备唯一编号
        self.device_type = ''   # 设备类型 gt310,..
        self.name = ''          # 设备名称
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

class WxUser(Model):
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''
        self.open_id = ''           # open_id
        self.nickName = ''
        self.gender = ''
        self.language = ''
        self.province = ''
        self.city =''
        self.country =''
        self.avatarUrl =''

class WxSystemInfo(Model):
    """微信手机系统信息"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''
        self.open_id =''
        self.brand = ''
        self.model = ''
        self.pixelRatio = ''
        self.screenWidth = ''
        self.screenHeight =''
        self.windowWidth = ''
        self.windowHeight = ''
        self.statusBarHeight = ''
        self.language =''
        self.version  =''
        self.system =''
        self.platform = ''
        self.fontSizeSetting =''
        self.SDKVersion = ''



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

class SharedDeviceLink(Model):
    """用户设备的分享控制，每个设备默认都有，且打开"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''       # 创建用户编号
        self.open_id = ''       # 分享的用户id
        self.device_id = ''     # 分享的设备
        self.device_type=''
        self.name = ''          # 分享的名称
        self.image =''
        self.expire_time = '2020-1-1'    # 分享到期时间 yyyy-mm-dd
        self.password = ''      # 访问密码（可以为空不设置)
        self.create_time = 0    # 创建时间
        self.user_limit = 0     # 访问限制
        self.status ='open'     # 默认打开 open,close
        self.share_code = ''    # 分享码,系统生成6位数字，输入分享码可直接录入设备，等同于转发朋友圈的功能
        self.code_update_time = 0 # 分享码更新时间

class ShareDeviceFollower(Model):
    """分享设备跟随者"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''       # follower 用户id
        self.open_id = ''       # follower 用户 wxid 冗余
        self.share_id = ''      # 分享id
        self.device_id = ''     # 设备id 冗余
        self.create_time = 0      # 加入时间
        self.denied = False     # 访问禁止
        self.avatar_url=''      # 头像信息
        self.nick_name =''      # 昵称


        # self.disable = False      # follower是否允许观看分享设备
        # self.disable_time = 0   # 禁用时间

        # 分享创建者可以随时关闭follower


#
# class SharedDeviceToTarget(Model):
#     """将设备分享给多个用户"""
#     def __init__(self):
#         Model.__init__(self)
#         self.share_device_id = ''   # SharedDevice
#         self.target_user_id = ''       # 分享的目标用户，微信用户
#         self.wx_link = ''           # 微信分享链接
#         self.code_2d = ''           # 二维码
#         self.message = ''           # 留言


class  Position(Model):
    """设备位置信息"""
    def __init__(self):
        Model.__init__(self)
        self.message_type = 'position'
        self.device_id = ''         # 设备编号
        self.device_type = ''       # 设备型号
        self.lon = 0                # 经度
        self.lat = 0                # 维度
        self.heading = 0            # 方向
        self.speed = 0              # 速度
        self.altitude = 0           # 海拔
        self.satellite = 0
        self.radius = 0             # lbs 定位的半径

        self.ymdhms = ''            #
        self.timestamp = 0          # gps 时间戳
        self.position_source = PositionSource.GPS           # 0:未知 , 1:gps,2:lbs,3:wifi
        self.coord_type = CoordinateType.WGS84         # 坐标类型 ， 0: unknown, 1:wgs84,2:bd,3:gd,4:tx
        # self.lon_bd = 0             # 百度坐标
        # self.lat_bd = 0             #
        # self.lon_gd = 0             # 高德坐标
        # self.lat_gd = 0
        # self.lon_tx = 0             # 腾讯坐标
        # self.lat_tx = 0
        self.address = ''           # 坐标转换的地址信息
        self.desc = ''

        self.mode = 'r'  # real or diff 实时还是差分  r / d
        self.located = 'y'  # y or n  是否已定位
        self.west_east = 'e'  # w or e  东经西经
        self.north_south = 'n'  # n or s

        self.mcc = 0
        self.mnc = 0
        self.lac = 0
        self.cell_id = 0
        self.rssi = 0
        self.signal = 0

        self.lac1 = 0
        self.ci1 = 0
        self.rssi1 = 0
        self.lac2 = 0
        self.ci2 = 0
        self.rssi2 = 0
        self.lac3 = 0
        self.ci3 = 0
        self.rssi3 = 0
        self.lac4 = 0
        self.ci4 = 0
        self.rssi4 = 0

        self.lac5 = 0
        self.ci5 = 0
        self.rssi5 = 0

        self.lac6 = 0
        self.ci6 = 0
        self.rssi6 = 0

        self.acc = 0
        self.report_mode = 0        # 上报模式
        self.up_mode = 0            # 上报实时、追加
        self.miles = 0              # 里程数
        # 2.
        self.oil_bit7 = 0           # 1:油电断开
        self.gps_bit6 = 0           # GPS 是否已定位
        self.charging_bit2 = 0      # 已接电源充电
        self.acc_bit1 = 1           # 1:ACC 高 , 0:ACC 低
        self.fortify_bit0 = 1       # 1:设防 , 0:撤防

        # 3.
        self.alarm = 0              # 报警类型
        self.alarm_name = ''        # 报警名称
        self.voltage = 0            # 电压
        self.gsm = 0                # 信号

        self.report_time = 0        # 报告时间 系统当前时间

class AlarmData(Position):
    """设备报警信息"""
    def __init__(self):
        Position.__init__(self)
        self.message_type = 'alarm'
        self.alarm_source_type = AlarmSourceType.EMPTY

class AudioRecord(Model):
    """录音数据"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''
        self.device_type = ''
        self.ymdhms = ''
        self.report_time = 0
        self.size  = 0
        self.content = ''  # base64 编码
        self.path = ''  #存储路径
        self.format='mp3'
        self.read_time = 0  # 已阅读时间

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

class Fence(Model):
    """围栏信息"""
    def __init__(self):
        Model.__init__(self)
        self.name =''           # 围栏名称
        self.device_id = ''     # 设备id
        self.device_type=''
        self.index = 0          # 围栏编号
        self.type = 'circle'    # circle or rect
        self.enable = 0
        self.cx = 0             # 中心点坐标
        self.cy = 0
        self.radius = 0
        self.x1 = 0             # 矩形围栏的左下坐标
        self.y1 = 0
        self.x2 = 0             # 右上坐标
        self.y2 = 0
        self.inout = ''         #in/out
        self.alarm_type = 1   #

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


        # self.ASETAPN = ''           # APN自适应
        # self.ASETGMT = ''           # 时区自适应
        # self.SERVER = ''            # 后台服务器参数设置
        # self.GMT = ''               # 时区设置
        # self.LANG = ''              # 语言设置
        # self.SOS = ''               # SOS号码设置
        # self.HBT = ''               # 心跳包设置间隔
        # self.ANGLEREP = ''          # 拐点补传设置
        # self.SENSOR = ''            # 震动检测时间
        # self.SENDS = ''            # SENSOR 控制 GPS 时间
        # self.GFENCE = ''            # 设置围栏报警
        # self.BATALM = ''            # 低电报警
        # self.SOSALM = ''            # SOS 报警
        # self.CALL = ''            # 电话重拨次数
        # self.LEVEL = ''            # SENSOR灵敏度设置
        # self.SENSORSET = ''        # 设置触发震动激活GPS工作条件
        # self.ALMREP = ''        # 设置接收报警号码（除SOS报警）
        # self.MODE = ''        # 模式设置（模式1、2）
        # self.ICCID = ''        # ICCID号点名查询
        # self.IMSI = ''        # IMSI
        # self.FIXMODE = ''        # 定位方式开关
        # self.FIXPRI = ''        # 定位方式优先级设置
        # self.FLY = ''        # 飞行状态开关


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



class Product(Model):
    """平台内销售的产品"""
    def __init__(self):
        Model.__init__(self)
        self.sku = ''       # 商品编码
        self.name = ''      # 商品名称
        self.category = ''  # 分类
        self.price = 0      # 价格
        self.description = '' # 描述
        self.url = ''       # 外连接介绍
        self.image_url = '' # 产品图片链接
        self.slide_image_url = '' # 滑动轮播产品链接
        self.content =''    # 可以做成是多图片的链接数组  a,b,c
        self.active = True  # 是否上架
        self.update_time = 0    # 更新时间

class Favorite(Model):
    """收藏夹"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''   # 用户编码
        self.sku = ''       # 商品编码
        self.number = 1     # 数量
        self.create_time = 0   # 加入时间
        self.order = 0      # 排序
        self.comment = ''   # 说明

class OrderProduct(Model):
    """订单商品表"""
    def __init__(self):
        Model.__init__(self)
        self.serial = ''    # 订单流水号
        self.sku = ''   # 商品编码
        self.number = 1 # 数量
        self.price = 0  # 单价
        self.amount = 0  # 总金额

class OrderStatus(Model):
    Inited = 'inited'  # 已创建未支付
    Payed = 'payed'      # 已支付
    Delivering= 'delivering'   # 运输中
    Finished = 'finish'    # 完成
    Cancelled = 'cancelled' # 取消

    def __init__(self):
        Model.__init__(self)
        self.user_id = ''
        self.serial = ''        # 订单编号
        self.issue_time  = 0    # 时间
        self.status = OrderStatus.Inited # 初始状态
        self.comment = ''       # 说明

class Order(Model):
    """订单记录"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''   # 用户编号
        self.serial = ''    # 订单流水号
        self.update_time = 0
        self.pay_serial = ''    #  支付流水
        self.pay_seller = ''    # 商家
        self.status = OrderStatus.Inited # 创建状态
        self.order = 0      # 排序
        self.cargo_address_id = ''  #收货地址记录


class CargoAddress(Model):
    """收货地址"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''       # 用户编号
        self.name = ''          # 收货人姓名
        self.phone = ''         # 电话
        self.address = ''       # 地址
        self.is_default = 0    # 是否缺省地址
        self.order = 0          # 排序
        self.update_time = 0    # 更新或创建时间

class LogShareLink(Model):
    """共享设备创建记录"""
    def __init__(self):
        Model.__init__(self)
        self.share_id = '' #  分享记录编号
        self.creator = ''  # 创建用户wx编号
        self.device_id = '' #设备编号
        self.name = ''      # 分享名称
        self.expire_time = 0
        self.password = ''
        self.create_time = 0
        self.user_limit = 0

class LogShareLinkAccept(Model):
    """分享设备用户接收记录,
        可以分析出用户之间的好友关系拓扑
        """
    def __init__(self):
        Model.__init__(self)
        self.share_id = '' # 分享记录
        self.device_id = '' #
        self.creator = '' # 分享创建者 open_id
        self.acceptor = '' # 接收设备的用户 open_id
        self.issue_time = 0 # 发生的时间

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

class LogAppBehavior(Model):
    """记录app端用户操作日志"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''   # user id 数据库记录id
        self.open_id = ''   # weixin
        self.platform =''   # 平台
        self.datetime =''   #
        self.timestamp = 0  #
        self.action_type = ''     # open,close,share,create,update,delete
        self.action_res_type = '' # 操作的资源对象类型
        self.action_res_id = ''   # 操作资源对象编号
        self.content = ''         # 描述

from mantis.fundamental.nosql.mongo import Connection
if __name__ == '__main__':
    conn = Connection().conn
    coll = conn['TradeLog_Ctp_htqh-01']['send_order']
    rs = coll.find()
    for r in rs :
        print r
    # print type(rs)