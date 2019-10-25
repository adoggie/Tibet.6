#coding:utf-8

import datetime
import struct

from mantis.BlueEarth.vendor.concox.gt03.message import *
from mantis.BlueEarth.vendor.concox.gt03.message import LocationData as _LocationData

from protocal import PacketType,MessageClsDict,TypeValue
from utils import ByteBuf
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fundamental.utils.useful import singleton

# from mantis.BlueEarth.vendor.concox.gt03.message import MessageBase,\
#     MessageLogin,AlarmType,LanguageValue,\
#     VoltageValue,GSMSignalValue,DeviceSimpleInfo,\
#     LocationReportMode,LocationData,\
#     MessageHeartBeat



# TIME_EAST = 0
# TIME_WEST = 1
#
# CONNECTED = 0
# DISCONNECT = 1
#
# GPS_YES = 1  # GPS 已定位
# GPS_NO = 0    # GPS 未定位
# ON = 1
# OFF = 0
# LOW =0
# HIGH = 1
#
# # GPS 实时补传
# GPS_UP_MODE_REAL = 0
# GPS_UP_MODE_DELAY = 1  # 0x00 实时上传 0x01 补传

class LocationData(_LocationData):
    def __init__(self):
        _LocationData.__init__(self)

    def parse_time(self,buf):
        y = 2000 + buf.read_uint8()
        m = buf.read_uint8()
        d = buf.read_uint8()
        h = buf.read_uint8()
        M = buf.read_uint8()
        s = buf.read_uint8()
        dt = datetime.datetime(y, m, d, h, M, s) + datetime.timedelta(hours=8)
        y = dt.year
        m = dt.month
        d = dt.day
        h = dt.hour
        M = dt.minute
        s = dt.second
        # self.ymdhms = '{}{}{} {}:{}:{}'.format(y,m,d,h,M,s)
        self.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)

class LocationDataExt(object):
    def __init__(self):
        # LocationData.__init__(self)

        self.mcc = 0
        self.mnc = 0
        self.lac = 0
        self.cell_id = 0
        # self.simple_info = DeviceSimpleInfo()
        # self.voltage = VoltageValue.EMPTY.value
        # self.gsm = GSMSignalValue.EMPTY.value
        # self.alarm = AlarmType.OK.value
        # self.lang = LanguageValue.CHINESE # 报警语言

    def dict(self):
        # data = self.simple_info.dict()
        data = {}
        data.update(hash_object(self,excludes=('simple_info',)))
        return data

    def from_dict(self,data):
        object_assign(self,data)
        # self.simple_info = DeviceSimpleInfo()
        # object_assign(self.simple_info,data)

    def parse(self,buf ):
        # LocationData.parse(self,buf)

        self.mcc = buf.read_uint16()
        self.mnc = buf.read_uint8()
        self.lac = buf.read_uint16()
        self.cell_id = tool_format_ci_value( buf.read_bytes(3))
        # self.simple_info.parse(buf.read_uint8())
        # self.voltage = buf.read_uint8()
        # self.gsm = buf.read_uint8()
        # self.alarm = buf.read_uint8()
        # self.lang = buf.read_uint8()

class MessageGpsLocation(MessageBase):
    """gps 定位包"""
    Type = PacketType.GpsLocation

    def __init__(self):
        MessageBase.__init__(self)
        self.location = LocationData()
        self.location_ext = LocationDataExt()

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
        msg.location_ext.parse(buf)

        msg.acc = buf.read_uint8()
        msg.rpt_mode = buf.read_uint8()
        msg.up_mode = buf.read_uint8()
        # msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = hash_object(self,excludes=('location','location_ext'))
        data.update(self.location.dict() )
        data.update(self.location_ext.dict())
        return data

    def from_dict(self,data):
        self.location.from_dict(data)
        self.location_ext.from_dict(data)
        self.acc = data.get('acc',LOW)
        self.rpt_mode = data.get('rpt_mode',LocationReportMode.T0.value)
        self.up_mode = data.get('up_mode',GPS_UP_MODE_REAL)
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
        self.ahead = 0  # 时间提前量
        self.lang = 0

    def parse_time(self,buf):
        y = 2000 + buf.read_uint8()
        m = buf.read_uint8()
        d = buf.read_uint8()
        h = buf.read_uint8()
        M = buf.read_uint8()
        s = buf.read_uint8()

        dt = datetime.datetime(y, m, d, h, M, s) + datetime.timedelta(hours=8)
        y = dt.year
        m = dt.month
        d = dt.day
        h = dt.hour
        M = dt.minute
        s = dt.second

        self.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)


    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageLbsStationExtension()
        msg.extra = extra

        # y = 2000 + buf.read_uint8()
        # m = buf.read_uint8()
        # d = buf.read_uint8()
        # h = buf.read_uint8()
        # M = buf.read_uint8()
        # s = buf.read_uint8()
        # msg.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)
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

        msg.ahead = buf.read_uint8()
        msg.lang = buf.read_uint16()

        return msg

# def tool_format_ci_value(bytes):
#     value = ''.join(map(lambda _:'%02x'%_,map(ord,bytes) ))
#     # value = '0'+bytes
#     value = int(value,16)
#     return value
#


class MessageDeviceRespOnlineCN(MessageBase):
    """ 在线地址回复
    todo. 未实现
    """
    Type = PacketType.DeviceRespOnlineCN

    def __init__(self):
        MessageBase.__init__(self)
        self.flag = ''  # [4] 标志
        self.encode = ''    # [1] 1：asc, 2: utf16
        self.content = ''   # [m]

    @staticmethod
    def unmarshall(bytes, extra=None):
        buf = ByteBuf(bytes)
        msg = MessageOnlineCommand()
        msg.extra = extra
        msg.flag = buf.read_uint32()
        msg.encode = buf.read_uint8()
        msg.content = buf.bytes[buf.index:]
        return msg

    def packet(self):
        from packet import NetWorkPacket
        pkt = NetWorkPacket()
        buf = ByteBuf()
        # size = 4 + len(self.content)
        # buf.write_uint8(size)
        # buf.write_uint32(self.sequence)
        # buf.write_bytes(self.content)
        # buf.write_uint16(self.lang)
        pkt.set_payload(buf.bytes)
        pkt.type = self.Type.value
        return pkt

    def parseContent(self):
        return parseContent(self.content)

def parseContent(content):
    """解析上报的设备信息，返回 kv 数据对"""
    data={}
    # print 'Content:',content
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
                t1,t2 = v.split(',')
                data['gps_timer'] = t1 #int(t3) * 60
                data['lbs_timer'] = t2 #int(t1) * 60

            if k ==  'SOS':
                p1,p2,p3 = v.split(',')
                data['sos_1'] = p1
                data['sos_2'] = p2
                data['sos_3'] = p3
                # data['sos_4'] = p4

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
    # gt310 - HBT:3min  这种格式，妈的
    if content.find(cap)==0:
        fs = content.split(':')

        idx = fs[1].find('min')
        if idx!=-1:
            min = fs[1][:idx] # gt310
        else:
            min = fs[1].split(',')[0] # ev25
        data['heartbeat_timer'] = int(min)

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


from mantis.BlueEarth.vendor.concox.gt03.message import MessageOnlineCommand as MessageOnlineCommand_
class MessageOnlineCommand(MessageOnlineCommand_):
    """在线设备发送命令"""
    Type = PacketType.OnlineCommandSet

    def __init__(self):
        MessageOnlineCommand_.__init__(self)

    def parseContent(self):
        """解析上报的设备信息，返回 kv 数据对"""
        return parseContent(self.content)

    #
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
    Type = PacketType.AlarmData

    def __init__(self):
        MessageBase.__init__(self)
        self.location = LocationData()
        self.lbs_size  = 0
        self.location_ext = LocationDataExt()

        self.simple_info = DeviceSimpleInfo()
        self.voltage = VoltageValue.EMPTY.value
        self.gsm = GSMSignalValue.EMPTY.value
        self.alarm = AlarmType.OK.value
        self.lang = LanguageValue.CHINESE # 报警语言
        self.miles = 0

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
        msg.lbs_size = buf.read_uint8()
        msg.location_ext.parse(buf)

        msg.simple_info.parse(buf.read_uint8())
        msg.voltage = buf.read_uint8()
        msg.gsm = buf.read_uint8()
        msg.alarm = buf.read_uint8()
        msg.lang = buf.read_uint8()
        msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = self.location.dict()
        data.update(self.location_ext.dict())
        data.update(hash_object(self,excludes=('location','location_ext')))
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
        object_assign(self,data)
        self.location_ext.from_dict(data)
        self.simple_info.from_dict(data)
        self.voltage = data.get('voltage',VoltageValue.EMPTY.value)
        self.gsm = data.get('gsm',GSMSignalValue.EMPTY.value)
        self.alarm = data.get('alarm',AlarmType.OK.value)
        self.lang = data.get('lang',LanguageValue.CHINESE)
        self.miles = data.get('miles',0)

class MessageFenceAlarm(MessageAlarmData):
    """多围栏报警"""
    Type = PacketType.FenceAlarm

    def __init__(self):
        MessageAlarmData.__init__(self)
        self.fence_id = 0  # 围栏编号

    # def response(self):
    #     """登录回复消息包序列化数据"""
    #     netpack = self.extra
    #     netpack.set_payload('')
    #     return netpack.to_bytes()

    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageFenceAlarm()
        msg.extra = extra

        msg.location.parse(buf)
        msg.lbs_size = buf.read_uint8()
        msg.location_ext.parse(buf)

        msg.simple_info.parse(buf.read_uint8())
        msg.voltage = buf.read_uint8()
        msg.gsm = buf.read_uint8()
        msg.alarm = buf.read_uint8()
        msg.lang = buf.read_uint8()

        msg.fence_id = buf.read_uint8()

        msg.miles = buf.read_uint32()
        return msg

    def dict(self):
        data = self.location.dict()
        data.update(self.location_ext.dict())
        data.update(hash_object(self, excludes=('location', 'location_ext')))
        data.update(self.simple_info.dict())
        data.update({
            'voltage': self.voltage,
            'gsm': self.gsm,
            'alarm': self.alarm,
            'lang': self.lang,
            'miles': self.miles,
            'fence_id': self.fence_id
        })
        return data

    def from_dict(self,data):
        self.location.from_dict(data)
        object_assign(self,data)
        self.location_ext.from_dict(data)
        self.simple_info.from_dict(data)
        self.voltage = data.get('voltage',VoltageValue.EMPTY.value)
        self.gsm = data.get('gsm',GSMSignalValue.EMPTY.value)
        self.alarm = data.get('alarm',AlarmType.OK.value)
        self.lang = data.get('lang',LanguageValue.CHINESE)
        self.miles = data.get('miles',0)
        self.fence_id = data.get('fence_id',0)


class MessageLbsAlarmData(MessageBase):
    """lbs 报警包"""
    Type = PacketType.LbsAlarm

    def __init__(self):
        MessageBase.__init__(self)
        self.location_ext = LocationDataExt()
        self.simple_info = DeviceSimpleInfo()
        self.voltage = VoltageValue.EMPTY.value
        self.gsm = GSMSignalValue.EMPTY.value
        self.alarm = AlarmType.OK.value
        self.lang = LanguageValue.CHINESE  # 报警语言

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
        msg.location_ext.parse(buf)
        msg.simple_info.parse(buf.read_uint8())
        msg.voltage = buf.read_uint8()
        msg.gsm = buf.read_uint8()
        msg.alarm = buf.read_uint8()
        msg.lang = buf.read_uint8()

        return msg

    def dict(self):
        data = self.location_ext.dict()
        data.update(hash_object(self, excludes=('location', 'location_ext')))
        return data

    def from_dict(self, data):
        object_assign(self, data)
        self.location_ext.from_dict(data)
        data.update(self.simple_info.dict())
        data.update({
            'voltage': self.voltage,
            'gsm': self.gsm,
            'alarm': self.alarm,
            'lang': self.lang
        })



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
        print '==',key
        registerMessageObject(value)

# print MessageClsDict.values()

# __all__ = (MessageHeartBeat,Message)