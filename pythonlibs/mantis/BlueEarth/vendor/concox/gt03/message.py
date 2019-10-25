#coding:utf-8

import datetime
import struct
from protocal import PacketType,MessageClsDict,TypeValue
from utils import ByteBuf
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.utils.useful import singleton

TIME_EAST = 0
TIME_WEST = 1

CONNECTED = 0
DISCONNECT = 1

GPS_YES = 1  # GPS 已定位
GPS_NO = 0    # GPS 未定位
ON = 1
OFF = 0
LOW =0
HIGH = 1

# GPS 实时补传
GPS_UP_MODE_REAL = 0
GPS_UP_MODE_DELAY = 1  # 0x00 实时上传 0x01 补传

class MessageBase(object):
    def __init__(self):
        self.extra = None
        self.name = ''

    def dict(self):
        data = hash_object(self,excludes=('extra','Type'))
        return data

    def from_dict(self, data):
        object_assign(self,data)

class DownStream(object):
    """下行命令"""
    def __init__(self):
        pass

    def packet(self):
        from packet import NetWorkPacketAllocator
        pkt = NetWorkPacketAllocator().createPacket()
        pkt.type = self.Type.value

class MessageLogin(MessageBase):
    """"""
    Type = PacketType.Login

    def __init__(self):
        MessageBase.__init__(self)
        self.device_id = ''
        self.device_type = 0
        self.timezone = 0
        self.eastwest = TIME_EAST
        self.language = 0

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        s = buf.read_bytes(8)
        msg = MessageLogin()
        msg.device_id = ''.join(map(lambda _:'%02x'%_,map(ord,s)))
        if msg.device_id[0] == '0':
            msg.device_id = msg.device_id[1:]
        value = buf.read_uint16()
        msg.eastwest = (value>>3) & 1
        msg.timezone = (value>>4) / 100
        msg.extra = extra
        return msg

    def dict(self):
        return hash_object(self)

    def from_dict(self,data):
        object_assign(self,data)


class LanguageValue(object):
    CHINESE = 1
    ENGLISH = 2
    def __init__(self):
        self.value = self.CHINESE

class AlarmType(object):
    OK = TypeValue(0x00,u'正常')
    SOS = TypeValue(0x01,u'SOS求救')
    POWER_OFF = TypeValue(0x02,u'断电报警')
    SHAKE = TypeValue(0x03,u'震动报警')
    FENCE_ENTER = TypeValue(0x04,u'进围栏报警')
    FENCE_LEAVE = TypeValue(0x05,u'出围栏报警')
    SPEED_OVER = TypeValue(0x06,u'超速报警')
    POSITION_MOVE = TypeValue(0x09,u'位移报警')
    BLIND_AREA_ENTER = TypeValue(0x0A,u'进GPS盲区报警')
    BLIND_AREA_LEAVE = TypeValue(0x0B,u'出GPS盲区报警')
    TURN_ON = TypeValue(0x0C,u'开机报警')
    FIRST_LOCATED = TypeValue(0x0D,u'GPS第一次定位报警')
    LOWER_POWER = TypeValue(0x0E,u'外电低电报警')
    LOWER_POWER_PROTECT =  TypeValue(0x0F,u'外电低电保护报警')

    CHANGE_SIMCARD = TypeValue(0x10,u'换卡报警')
    SHUTDOWN = TypeValue(0x11,u'关机报警')
    FLY_MODE = TypeValue(0x12,u'外电低电保护后飞行模式报警')
    DISMANTLE = TypeValue(0x13,u'拆卸报警')
    DOOR_ALARM = TypeValue(0x14,u'门报警')
    LOW_POWER_SHUTDOWN = TypeValue(0x15,u'低电关机报警')
    SOUND_ALARM = TypeValue(0x16,u'声控报警')
    FAKE_STATION = TypeValue(0x17,u'伪基站报警')
    OPEN_BOX = TypeValue(0x18,u'开盖报警')
    BATTERY_LOW = TypeValue(0x19,u'内部电池低电报警')
    START_SLEEP = TypeValue(0x20,u'进入深度休眠报警')
    # 0x21预留
    # 0x22预留
    FALL = TypeValue(0x23,u'跌倒报警')
    # 0x24预留
    LIGHT_ALARM = TypeValue(0x25,u'光感报警')
    SHUTDOWN_2 = TypeValue(0x28,u'主动离线(关机)报警')
    SPEED_UP_ACCEL = TypeValue(0x29,u'急加速')
    TURN_LEFT = TypeValue(0x2A,u'左急转弯报警')
    TURN_RIGHT = TypeValue(0x2B,u'右急转弯报警')
    COLLISION = TypeValue(0x2C,u'碰撞报警')
    SPEED_DOWN_ACCEL = TypeValue(0x30,u'急减速')
    GROUP_LEAVE = TypeValue(0x31,u'离群报警')

    FLIP = TypeValue(0x32,u'拔除翻转报警')
    LOCK = TypeValue(0x33,u'上锁锁上报')
    UNLOCK = TypeValue(0x34,u'开锁上报')

    UNLOCK_UNNORMAL = TypeValue(0x35,u'异常开锁报警')

    UNLOCK_FAIL = TypeValue(0x36,u'开锁失败报警')
    ACC_ON = TypeValue(0xFF,u'ACC关')
    ACC_OFF = TypeValue(0xFE,u'ACC开')

    table = {}

    @staticmethod
    def init_table():
        attrs = [s for s in dir(AlarmType) if not s.startswith('__')]
        for k in attrs:
            attr = getattr(AlarmType,k)
            if not callable(attr) and not isinstance(attr,dict):
                # print k,attr
                AlarmType.table[attr.value] = attr

    @staticmethod
    def get_name(type_id):
        alarm = AlarmType.table.get(type_id)
        name = ''
        if alarm:
            name = alarm.comment
        return name


AlarmType.init_table()

class VoltageValue(object):
    EMPTY = TypeValue(0x00,u'无电(关机)')
    L1 = TypeValue(0x01,u'电量极低(不足以打电话发短信等)')
    L2 = TypeValue(0x02,u'电量很低(低电报警)')
    L3 = TypeValue(0x03,u'电量低(可正常使用)')
    L4 = TypeValue(0x04,u'电量中')
    L5 = TypeValue(0x05,u'电量高')
    L6 = TypeValue(0x06,u'电量极高')
    # 设备电压百分比显示参考:6=100% 5=70% 4=40% 3=15% 2=5% 1=1%
    def __init__(self):
        self.value = self.EMPTY

class GSMSignalValue(object):
    EMPTY = TypeValue(0x00,u'无信号')
    L1 = TypeValue(0x01,u'信号极弱')
    L2 = TypeValue(0x02,u'信号较弱')
    L3 = TypeValue(0x03,u'信号良好')
    L4 = TypeValue(0x04,u'信号强')
    def __init__(self):
        self.value = self.EMPTY

class DeviceSimpleInfo(object):
    def __init__(self):
        self.oil_bit7 = DISCONNECT  # 1:油电断开
        self.gps_bit6 = GPS_NO      # GPS 是否已定位
        self.charging_bit2 = CONNECTED  # 已接电源充电
        self.acc_bit1 = HIGH          # 1:ACC 高 , 0:ACC 低
        self.fortify_bit0 = ON      # 1:设防 , 0:撤防

    def parse(self,byte):
        self.oil_bit7 = byte >> 7
        self.gps_bit6 = (byte >> 6) & 1
        self.charging_bit2 = (byte >> 2) & 1
        self.acc_bit1 = (byte >> 1) & 1
        self.fortify_bit0 = byte & 1

    def dict(self):
        return hash_object(self)

    def from_dict(self,data):
        object_assign(self,data)

class LocationReportMode(object):
    """数据点上报类型"""
    T0 = TypeValue(0x00,u'定时上报')
    T1 = TypeValue(0x01,u'定距上报')
    T2 = TypeValue(0x02,u'拐点上传')
    T3 = TypeValue(0x03,u'ACC 状态改变上传')
    T4 = TypeValue(0x04,u'从运动变为静止状态后，补传最后一个定位点')
    T5 = TypeValue(0x05,u'网络断开重连后，上报之前最后一个有效上传点')
    T6 = TypeValue(0x06,u'上报模式:星历更新强制上传 GPS 点')
    T7 = TypeValue(0x07,u'上报模式:按键上传定位点')
    T8 = TypeValue(0x08,u'上报模式:开机上报位置信息')
    T9 = TypeValue(0x09,u'上报模式:未使用')
    Ta = TypeValue(0x0a,u'上报模式:设备静止后上报最后的经纬度，但时间更新')
    Tb = TypeValue(0x0b,u'WIFI 解析经纬度上传包')
    Tc = TypeValue(0x0c,u'上报模式:LJDW(立即定位)指令上报')
    Td = TypeValue(0x0d,u'上报模式:设备静止后上报最后的经纬度')
    Te = TypeValue(0x0e,u'上报模式:GPSDUP 上传(下静止状态定时上传)')
    def __init__(self):
        self.value = self.T0

class LocationData(object):
    def __init__(self):
        self.ymdhms = ''
        self.satellite = 0
        self.lon = 0
        self.lat = 0
        self.speed = 0
        self.heading = 0

        self.mode = 'r' # real or diff 实时还是差分  r / d
        self.located = 'y'  # y or n  是否已定位
        self.west_east= 'e'        # w or e  东经西经
        self.north_south = 'n'     # n or s

        # self.mcc = 0
        # self.mnc = 0
        # self.lac = 0
        # self.cell_id = 0
        # self.lang = 0

    def dict(self):
        return hash_object(self)

    def from_dict(self,data):
        object_assign(self,data)

    def parse_time(self,buf):
        y = 2000 + buf.read_uint8()
        m = buf.read_uint8()
        d = buf.read_uint8()
        h = buf.read_uint8()
        M = buf.read_uint8()
        s = buf.read_uint8()
        # dt = datetime.datetime(y, m, d, h, M, s) + datetime.timedelta(hours=8)
        # y = dt.year
        # m = dt.month
        # d = dt.day
        # h = dt.hour
        # M = dt.minute
        # s = dt.second
        # self.ymdhms = '{}{}{} {}:{}:{}'.format(y,m,d,h,M,s)
        self.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)

    def parse(self,buf ):
        # y = 2000 + buf.read_uint8()
        # m = buf.read_uint8()
        # d = buf.read_uint8()
        # h = buf.read_uint8()
        # M = buf.read_uint8()
        # s = buf.read_uint8()
        # dt = datetime.datetime(y,m,d,h,M,s) + datetime.timedelta(hours=8)
        # y = dt.year
        # m = dt.month
        # d = dt.day
        # h = dt.hour
        # M = dt.minute
        # s = dt.second
        # # self.ymdhms = '{}{}{} {}:{}:{}'.format(y,m,d,h,M,s)
        # self.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)
        self.parse_time(buf)

        ui8 = buf.read_uint8()
        v = [ (ui8>>4) & 0xf,(ui8 & 0xf)]
        # self.satellite = '%s %s'% tuple(v)
        self.satellite = v[1]
        self.lat = buf.read_uint32()/1800000.
        self.lon = buf.read_uint32() / 1800000.
        self.speed = buf.read_uint8()
        ui16 = buf.read_uint16()
        self.heading = ui16 & 0b1111111111

        self.north_south = 's'
        if (ui16>>10) & 0x01 :
            self.north_south = 'n'

        self.west_east = 'w'
        if (ui16>>11) & 0x01 == 0:
            self.west_east = 'e'

        self.located = 'n'
        if (ui16>>12) & 0x01 == 1:
            self.located = 'y'

        self.mode = 'd'
        if (ui16>>13) & 0x01 == 0 :
            self.mode = 'r'

        # self.mcc = buf.read_uint16()
        # self.mnc = buf.read_uint8()
        # self.lac = buf.read_uint16()
        # v = buf.read_bytes(3)
        # self.cell_id =v
        # self.lang = buf.read_uint16()

        # print self.__dict__

class LocationDataExt(object):
    def __init__(self):
        # LocationData.__init__(self)

        self.mcc = 0
        self.mnc = 0
        self.lac = 0
        self.cell_id = 0
        self.simple_info = DeviceSimpleInfo()
        self.voltage = VoltageValue.EMPTY.value
        self.gsm = GSMSignalValue.EMPTY.value
        self.alarm = AlarmType.OK.value
        self.lang = LanguageValue.CHINESE # 报警语言

    def dict(self):
        data = self.simple_info.dict()
        data.update(hash_object(self,excludes=('simple_info',)))
        return data

    def from_dict(self,data):
        object_assign(self,data)
        self.simple_info = DeviceSimpleInfo()
        object_assign(self.simple_info,data)

    def parse(self,buf ):
        # LocationData.parse(self,buf)

        self.mcc = buf.read_uint16()
        self.mnc = buf.read_uint8()
        self.lac = buf.read_uint16()
        self.cell_id = tool_format_ci_value( buf.read_bytes(3))
        self.simple_info.parse(buf.read_uint8())
        self.voltage = buf.read_uint8()
        self.gsm = buf.read_uint8()
        self.alarm = buf.read_uint8()
        self.lang = buf.read_uint8()


class MessageGpsLocation(MessageBase):
    """gps 定位包"""
    Type = PacketType.GpsLocation

    def __init__(self):
        MessageBase.__init__(self)
        self.location = LocationData()



        # self.acc = LOW
        # self.rpt_mode = LocationReportMode.T0.value  # 上报模式
        # self.up_mode = GPS_UP_MODE_REAL  # 上报实时、追加
        # self.miles = 0  # 里程数

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageGpsLocation()
        msg.extra = extra
        msg.location.parse(buf)

        # msg.acc = buf.read_uint8()
        # msg.rpt_mode = buf.read_uint8()
        # msg.up_mode = buf.read_uint8()
        # msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = hash_object(self,excludes=('location',))
        data.update(self.location.dict() )
        return data

    def from_dict(self,data):
        self.location.from_dict(data)
        # self.acc = data.get('acc',LOW)
        # self.rpt_mode = data.get('rpt_mode',LocationReportMode.T0.value)
        # self.up_mode = data.get('up_mode',GPS_UP_MODE_REAL)
        # self.miles = data.get('miles',0)


class MessageLbsStationExtension(MessageBase):
    """基站定位包
    460	1	9649	28657	23.1067600250244	114.416069030762	广东省惠州市惠城区江北街道水北
    """
    Type = PacketType.LbsStationExtension

    def __init__(self):
        MessageBase.__init__(self)
        self.ymdhms = ''
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

        self.lang = 0

    def parse_time(self,buf):
        y = 2000 + buf.read_uint8()
        m = buf.read_uint8()
        d = buf.read_uint8()
        h = buf.read_uint8()
        M = buf.read_uint8()
        s = buf.read_uint8()

        # dt = datetime.datetime(y, m, d, h, M, s) + datetime.timedelta(hours=8)
        # y = dt.year
        # m = dt.month
        # d = dt.day
        # h = dt.hour
        # M = dt.minute
        # s = dt.second

        self.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageLbsStationExtension()
        msg.extra = extra

        msg.parse_time(buf)

        msg.mcc = buf.read_uint16()
        msg.mnc = buf.read_uint8()
        msg.lac = buf.read_uint16()
        msg.cell_id = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi = buf.read_uint8()
        msg.signal = msg.rssi

        msg.lac1 = buf.read_uint16()
        msg.ci1 = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi1 = buf.read_uint8()

        msg.lac2 = buf.read_uint16()
        msg.ci2 = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi2 = buf.read_uint8()

        msg.lac3 = buf.read_uint16()
        msg.ci3 = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi3 = buf.read_uint8()

        msg.lac4 = buf.read_uint16()
        msg.ci4 = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi4 = buf.read_uint8()

        msg.lac5 = buf.read_uint16()
        msg.ci5 = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi5 = buf.read_uint8()

        msg.lac6 = buf.read_uint16()
        msg.ci6 = tool_format_ci_value( buf.read_bytes(3))
        msg.rssi6 = buf.read_uint8()

        return msg

def tool_format_ci_value(bytes):
    value = ''.join(map(lambda _:'%02x'%_,map(ord,bytes) ))
    # value = '0'+bytes
    value = int(value,16)
    return value

class MessageHeartBeat(MessageBase):
    """"""
    Type = PacketType.HeartBeat

    def __init__(self):
        MessageBase.__init__(self)
        self.simple_info    = DeviceSimpleInfo()
        self.voltage        = VoltageValue.EMPTY.value
        self.gsm            = GSMSignalValue.EMPTY.value
        self.lang           = LanguageValue.CHINESE

    def response(self):
        """回复心跳消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageHeartBeat()
        msg.extra = extra
        msg.simple_info.parse(buf.read_uint8())
        msg.voltage = buf.read_uint8()
        msg.gsm = buf.read_uint8()
        msg.lang = buf.read_uint16()
        return msg

    def dict(self):
        data = self.simple_info.dict()
        data.update({'voltage':self.voltage,
                     'gsm':self.gsm,
                     'lang':self.lang
                     })
        return data

    def from_dict(self,data):
        self.simple_info.from_dict(data)
        self.voltage = data.get('voltage',VoltageValue.EMPTY.value)
        self.gsm = data.get('gsm',GSMSignalValue.EMPTY.value)
        self.lang = data.get('lang',LanguageValue.CHINESE)


# class MessageDeviceRespOnlineCN(MessageBase):
#     """"""
#     Type = PacketType.DeviceRespOnlineCN
#
#     def __init__(self):
#         MessageBase.__init__(self)
#
#     def response(self):
#         """登录回复消息包序列化数据"""
#         netpack = self.extra
#         netpack.set_payload('')
#         return netpack.to_bytes()
#
#     @staticmethod
#     def unmarshall(bytes,extra=None):
#         buf = ByteBuf(bytes)
#         msg = MessageDeviceRespOnlineCN()
#         msg.extra = extra
#         return msg

# class MessageDeviceRespOnlineEN(MessageBase):
#     """"""
#     Type = PacketType.DeviceRespOnlineEN
#
#     def __init__(self):
#         MessageBase.__init__(self)
#
#     def response(self):
#         """登录回复消息包序列化数据"""
#         netpack = self.extra
#         netpack.set_payload('')
#         return netpack.to_bytes()
#
#     @staticmethod
#     def unmarshall(bytes,extra=None):
#         buf = ByteBuf(bytes)
#         msg = MessageDeviceRespOnlineEN()
#         msg.extra = extra
#         return msg

class MessageAlarmData(MessageBase):
    """gps 报警消息包"""
    Type = PacketType.GpsAlarm

    def __init__(self):
        MessageBase.__init__(self)
        self.location = LocationData()
        self.lbs_size  = 0
        self.location_ext = LocationDataExt()

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')

        if self.location_ext.lang == LanguageValue.CHINESE:
            netpack.type = PacketType.AddressCNResp.value
            msg = MessageAddressCNResp()
            netpack.set_payload(msg.marshall())
        elif self.location_ext.lang == LanguageValue.ENGLISH:
            netpack.type = PacketType.AddressENResp.value
            msg = MessageAddressENResp()
            netpack.set_payload(msg.marshall())

        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageAlarmData()
        msg.extra = extra
        msg.location.parse(buf)
        msg.lbs_size = buf.read_uint8()
        msg.location_ext.parse(buf)


        # msg.simple_info.parse(buf.read_uint8())
        # msg.voltage = buf.read_uint8()
        # msg.gsm = buf.read_uint8()
        # msg.alarm = buf.read_uint8()
        # msg.lang = buf.read_uint8()
        # msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = self.location.dict()
        data.update(self.location_ext.dict())
        data.update(hash_object(self,excludes=('location','location_ext')))
        # data.update(self.simple_info.dict())
        # data.update({
        #     'voltage':self.voltage,
        #     'gsm':self.gsm,
        #     'alarm':self.alarm,
        #     'lang':self.lang,
        #     'miles':self.miles
        # })
        return data

    def from_dict(self,data):
        self.location.from_dict(data)
        object_assign(self,data)
        self.location_ext.from_dict(data)
        # self.simple_info.from_dict(data)
        # self.voltage = data.get('voltage',VoltageValue.EMPTY.value)
        # self.gsm = data.get('gsm',GSMSignalValue.EMPTY.value)
        # self.alarm = data.get('alarm',AlarmType.OK.value)
        # self.lang = data.get('lang',LanguageValue.CHINESE)
        # self.miles = data.get('miles',0)

# class MessageFenceAlarm(MessageBase):
#     """"""
#     Type = PacketType.FenceAlarm
#
#     def __init__(self):
#         MessageBase.__init__(self)
#
#     def response(self):
#         """登录回复消息包序列化数据"""
#         netpack = self.extra
#         netpack.set_payload('')
#         return netpack.to_bytes()
#
#     @staticmethod
#     def unmarshall(bytes,extra=None):
#         buf = ByteBuf(bytes)
#         msg = MessageFenceAlarm()
#         msg.extra = extra
#
#         return msg

class MessageLbsAlarmData(MessageBase):
    """lbs 报警包"""
    Type = PacketType.LbsAlarm

    def __init__(self):
        MessageBase.__init__(self)
        self.location_ext = LocationDataExt()

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')

        if self.location_ext.lang == LanguageValue.CHINESE:
            netpack.type = PacketType.AddressCNResp.value
            msg = MessageAddressCNResp()
            netpack.set_payload(msg.marshall())
        elif self.location_ext.lang == LanguageValue.ENGLISH:
            netpack.type = PacketType.AddressENResp.value
            msg = MessageAddressENResp()
            netpack.set_payload(msg.marshall())

        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageLbsAlarmData()
        msg.extra = extra
        return msg

    def dict(self):
        data = self.location_ext.dict()
        data.update(hash_object(self, excludes=('location', 'location_ext')))
        return data

    def from_dict(self, data):
        object_assign(self, data)
        self.location_ext.from_dict(data)

# class MessageGpsAddressReq(MessageBase):
#     """"""
#     Type = PacketType.GpsAddressReq
#
#     def __init__(self):
#         MessageBase.__init__(self)
#
#     def response(self):
#         """登录回复消息包序列化数据"""
#         netpack = self.extra
#         netpack.set_payload('')
#         return netpack.to_bytes()
#
#     @staticmethod
#     def unmarshall(bytes,extra=None):
#         buf = ByteBuf(bytes)
#         msg = MessageGpsAddressReq()
#         msg.extra = extra
#         return msg


# class MessageLbsAddressReq(MessageBase):
#     """"""
#     Type = PacketType.LbsAddressReq
#
#     def __init__(self):
#         MessageBase.__init__(self)
#
#     def response(self):
#         """登录回复消息包序列化数据"""
#         netpack = self.extra
#         netpack.set_payload('')
#         return netpack.to_bytes()
#
#     @staticmethod
#     def unmarshall(bytes,extra=None):
#         buf = ByteBuf(bytes)
#         msg = MessageLbsAddressReq()
#         msg.extra = extra
#         return msg

class MessageOnlineCommand(MessageBase,DownStream):
    """在线设备发送命令"""
    Type = PacketType.OnlineCommandSet

    def __init__(self,sequence=0,content='',lang = 0x01):
        MessageBase.__init__(self)
        self.sequence = sequence
        self.content = content
        self.lang = lang

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageOnlineCommand()
        msg.extra = extra
        size = buf.read_uint8()
        body_size = size - 4
        msg.sequence = buf.read_uint32()
        msg.content = buf.read_bytes(body_size)
        msg.lang = buf.read_uint16()
        return msg

    def packet(self):
        from packet import NetWorkPacket
        pkt = NetWorkPacket()
        buf = ByteBuf()
        size = 4 + len(self.content)
        buf.write_uint8(size)
        buf.write_uint32(self.sequence)
        buf.write_bytes(self.content)
        buf.write_uint16(self.lang)
        pkt.set_payload(buf.bytes)
        pkt.type = self.Type.value
        return pkt

    def parseContent(self):
        return parseContent(self.content)

def parseContent(content):
    """解析上报的设备信息，返回 kv 数据对"""
    data={}
    print 'Content:',content
    cap = '[VERSION]'
    if content.find(cap) == 0:
        ver = content.split(cap)[-1]
        data['ver'] = ver

    cap = 'IMEI:'
    if content.find(cap) == 0:
        items = map(lambda  _:_.strip(),content.split(';'))
        items = filter(lambda _:_,items)
        kvs = dict(map(lambda _:_.split(":"),items))
        for k,v in kvs.items():
            if k =='IMEI':
                data['imei'] = v
            if k=='TIMER':
                t1,t2,t3 = v.split(',')
                data['gps_timer'] = t3 #int(t3) * 60
                data['lbs_timer'] = t1 #int(t1) * 60
            if k ==  'SOS':
                p1,p2,p3,p4 = v.split(',')
                data['sos_1'] = p1
                data['sos_2'] = p2
                data['sos_3'] = p3
                data['sos_4'] = p4

    cap = 'SERVER'
    if content.find(cap) == 0:
        fs = content.split(',')
        if fs[1] == '1':
            data['server_mode'] = 'domain'
            data['server_domain'] = fs[2]
        else:
            data['server_ip'] = fs[2]
        data['server_port'] = fs[3]

    cap ='HBT'
    if content.find(cap)==0:
        fs = content.split(':')
        data['heartbeat_timer'] = int(fs[1])

    cap = 'FenceType'
    if content.find(cap) == 0:
        items = map(lambda _: _.strip(), content.split(','))
        onoff = items[1].lower()
        del items[1]
        kvs = dict(map(lambda _: _.split(":"), items))
        data['fence_enable'] = onoff

        for k, v in kvs.items():
            if k == 'FenceType':
                data['fence_type'] = v.lower()
            if k=='Latitude':
                data['fence_cy'] = v
            if k=='Longitude':
                data['fence_cx'] = v
            if k=='radius':
                data['fence_radius'] = v[0:-1]
            if k=='in out':
                data['fence_inout'] = v
            if k == 'alarm type':
                data['fence_alarm_type'] = v
    return data

class MessageOnlineCommandQuery(MessageOnlineCommand):
    """在线设备发送查询命令"""
    Type = PacketType.OnlineCommandResponse
    def __init__(self):
        MessageOnlineCommand.__init__(self)

# class MessageOnlineCommandSet(MessageOnlineCommand):
#     """在线设备发送设置命令"""
#     Type = PacketType.OnlineCommandSet
#     def __init__(self):
#         MessageOnlineCommand.__init__(self)

class MessageAdjustTime(MessageBase):
    """校时包"""
    Type = PacketType.AdjustTime

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        now = datetime.datetime.now()
        year = now.year - 2000
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        data = struct.pack('B'*6,year,month,day,hour,minute,second)
        netpack.set_payload(data)
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageAdjustTime()
        msg.extra = extra
        return msg



class MessageGenericMessage(MessageBase):
    """信息传输通用包"""
    Type = PacketType.GenericMessage

    def __init__(self):
        MessageBase.__init__(self)
        self.type = 0   # 信息类型
        self.content = ''   # 信息内容 文本AT指令风格

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        import base64
        buf = ByteBuf(bytes)
        msg = MessageGenericMessage()
        msg.extra = extra
        msg.type = buf.read_uint8()
        msg.content = buf.bytes[buf.index:]
        if msg.type == 4: # 终端状态同步信息 ascii
            pass
        else: # 转成 base64
            msg.content = base64.b64encode(msg.content)
        return msg



class MessageAddressCNResp(MessageBase):
    """"""
    Type = PacketType.AddressCNResp

    def __init__(self):
        MessageBase.__init__(self)
        self.size = 0
        self.sequence = 0
        self.alarmsms = 'X'*8
        self.address = ''
        self.tel = '0'*21

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageAddressCNResp()
        msg.extra = extra
        return msg

    def marshall(self):
        buf = ByteBuf()
        self.size = 39 + len(self.address)
        buf.write_uint8(self.size)
        buf.write_uint32(self.sequence)
        buf.write_bytes(self.alarmsms)
        buf.write_bytes('&&')
        buf.write_bytes(self.address)
        buf.write_bytes('&&')
        buf.write_bytes(self.tel)
        buf.write_bytes('##')
        return buf.bytes

class MessageAddressENResp(MessageAddressCNResp):
    """"""
    Type = PacketType.AddressENResp

    def __init__(self):
        MessageAddressCNResp.__init__(self)

def registerMessageObject(msgcls):
    MessageClsDict[msgcls.Type.value] = msgcls

# print globals().keys()
for key,value in locals().items():
    if key.find('Message')==0 and key not in ('MessageClsDict','MessageBase'):
        registerMessageObject(value)

# print MessageClsDict.values()


# @singleton
# class MessageOnlineCommandAllocator(object):
#     def __init__(self):
#         self.seq_gen = None
#
#     def setSequenceGeneroator(self,generator):
#         self.seq_gen = generator
#
#     def createCommand(self):
#         cmd = MessageOnlineCommand(self.seq_gen.next())
#         return cmd

