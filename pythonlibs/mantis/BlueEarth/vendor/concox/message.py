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
        msg.device_id = ''.join(map(hex,map(ord,s))).replace('0x','')
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
        self.satellite = ''
        self.lon = 0
        self.lat = 0
        self.speed = 0
        self.heading = 0
        self.mcc = 0
        self.mnc = 0
        self.lac = 0
        self.cell_id = 0

    def dict(self):
        return hash_object(self)

    def from_dict(self,data):
        object_assign(self,data)

    def parse(self,buf ):
        y = 2000 + buf.read_uint8()
        m = buf.read_uint8()
        d = buf.read_uint8()
        h = buf.read_uint8()
        M = buf.read_uint8()
        s = buf.read_uint8()
        self.ymdhms = '{}{}{} {}:{}:{}'.format(y,m,d,h,M,s)
        ui8 = buf.read_uint8()
        self.satellite = [(ui8>>4 & 0xf),ui8 & 0xf]
        self.lat = buf.read_uint32()/1800000.
        self.lon = buf.read_uint32() / 1800000.
        self.speed = buf.read_uint8()
        ui16 = buf.read_uint16()
        self.heading = ui16 & 0b1111111111
        self.mcc = buf.read_uint16()
        self.mnc = buf.read_uint8()
        self.lac = buf.read_uint16()
        v = buf.read_bytes(3)
        self.cell_id =v

        # print self.__dict__


class MessageGpsLocation(MessageBase):
    """"""
    Type = PacketType.GpsLocation

    def __init__(self):
        MessageBase.__init__(self)
        self.location = LocationData()
        self.acc = LOW
        self.rpt_mode = LocationReportMode.T0.value  # 上报模式
        self.up_mode = GPS_UP_MODE_REAL  # 上报实时、追加
        self.miles = 0  # 里程数

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageGpsLocation()
        msg.extra = extra
        msg.location.parse(buf)
        msg.acc = buf.read_uint8()
        msg.rpt_mode = buf.read_uint8()
        msg.up_mode = buf.read_uint8()
        msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = hash_object(self,excludes=('location',))
        data.update(self.location.dict() )
        return data

    def from_dict(self,data):
        self.location.from_dict(data)
        self.acc = data.get('acc',LOW)
        self.rpt_mode = data.get('rpt_mode',LocationReportMode.T0.value)
        self.up_mode = data.get('up_mode',GPS_UP_MODE_REAL)
        self.miles = data.get('miles',0)

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


class MessageDeviceRespOnlineCN(MessageBase):
    """"""
    Type = PacketType.DeviceRespOnlineCN

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageDeviceRespOnlineCN()
        msg.extra = extra
        return msg

class MessageDeviceRespOnlineEN(MessageBase):
    """"""
    Type = PacketType.DeviceRespOnlineEN

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageDeviceRespOnlineEN()
        msg.extra = extra
        return msg

class MessageAlarmData(MessageBase):
    """gps 报警消息包"""
    Type = PacketType.AlarmData

    def __init__(self):
        MessageBase.__init__(self)
        self.location = LocationData()
        self.simple_info    = DeviceSimpleInfo()
        self.voltage = VoltageValue.EMPTY.value
        self.gsm = GSMSignalValue.EMPTY.value
        self.alarm = AlarmType.OK.value
        self.lang = LanguageValue.CHINESE
        self.miles = 0  # 里程数

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')

        if self.lang == LanguageValue.CHINESE:
            netpack.type = PacketType.AddressCNResp.value
            msg = MessageAddressCNResp()
            netpack.set_payload(msg.marshall())
        elif self.lang == LanguageValue.ENGLISH:
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
        msg.simple_info.parse(buf.read_uint8())
        msg.voltage = buf.read_uint8()
        msg.gsm = buf.read_uint8()
        msg.alarm = buf.read_uint8()
        msg.lang = buf.read_uint8()
        msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = self.location.dict()
        data.update(self.simple_info.dict())
        data.update({
            'voltage':self.voltage,
            'gsm':self.gsm,
            'alarm':self.alarm,
            'lang':self.lang,
            'miles':self.miles
        })
        return data

    def from_dict(self,data):
        self.location.from_dict(data)
        self.simple_info.from_dict(data)
        self.voltage = data.get('voltage',VoltageValue.EMPTY.value)
        self.gsm = data.get('gsm',GSMSignalValue.EMPTY.value)
        self.alarm = data.get('alarm',AlarmType.OK.value)
        self.lang = data.get('lang',LanguageValue.CHINESE)
        self.miles = data.get('miles',0)

class MessageFenceAlarm(MessageBase):
    """"""
    Type = PacketType.FenceAlarm

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageFenceAlarm()
        msg.extra = extra

        return msg

class MessageLbsAlarm(MessageBase):
    """"""
    Type = PacketType.LbsAlarm

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageLbsAlarm()
        msg.extra = extra
        return msg

class MessageGpsAddressReq(MessageBase):
    """"""
    Type = PacketType.GpsAddressReq

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageGpsAddressReq()
        msg.extra = extra
        return msg


class MessageLbsAddressReq(MessageBase):
    """"""
    Type = PacketType.LbsAddressReq

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageLbsAddressReq()
        msg.extra = extra
        return msg

class MessageOnlineCommand(MessageBase,DownStream):
    """在线设备发送命令"""
    Type = PacketType.OnlineCommand

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
        return msg

    def packet(self):
        pkt = DownStream.packet()
        buf = ByteBuf()
        size = 4 + len(self.content)
        buf.write_uint8(size)
        buf.write_uint32(self.sequence)
        buf.write_bytes(self.content)
        buf.write_uint16(self.lang)
        pkt.set_payload(buf.bytes)


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
    """"""
    Type = PacketType.GenericMessage

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageGenericMessage()
        msg.extra = extra
        return msg

class MessageAddressCNResp(MessageBase):
    """"""
    Type = PacketType.AddressCNResp

    def __init__(self):
        MessageBase.__init__(self)

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
        return ''

class MessageAddressENResp(MessageBase):
    """"""
    Type = PacketType.AddressENResp

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageAddressENResp()
        msg.extra = extra
        return msg

    def marshall(self):
        return ''

class MessageSerialUpStream(MessageBase):
    """"""
    Type = PacketType.SerialUpStream

    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageSerialUpStream()
        msg.extra = extra
        return msg

class MessageSerialDownStream(MessageBase):
    """"""
    Type = PacketType.SerialDownStream
    def __init__(self):
        MessageBase.__init__(self)

    def response(self):
        """登录回复消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageSerialDownStream()
        msg.extra = extra
        return msg

# MessageClsDict[MessageLogin.Type.value] = MessageLogin

def registerMessageObject(msgcls):
    MessageClsDict[msgcls.Type.value] = msgcls

# print globals().keys()
for key,value in locals().items():
    if key.find('Message')==0 and key not in ('MessageClsDict','MessageBase'):
        registerMessageObject(value)

# print MessageClsDict.values()


@singleton
class MessageOnlineCommandAllocator(object):
    def __init__(self):
        self.seq_gen = None

    def setSequenceGeneroator(self,generator):
        self.seq_gen = generator

    def createCommand(self):
        cmd = MessageOnlineCommand(self.seq_gen.next())
        return cmd

