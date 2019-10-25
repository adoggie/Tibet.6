#coding:utf-8

import datetime
import struct
from mantis.BlueEarth.vendor.concox.ev25.message import *
from protocal import PacketType,MessageClsDict,TypeValue
from utils import ByteBuf
from mantis.fundamental.utils.useful import hash_object,object_assign


class WifiData(object):
    def __init__(self):
        self.signal =0  # 信号强度
        self.mac = 0    # mac 地址

    def dict(self):
        data = {'signal':self.signal,
                'mac':self.mac
                }
        return data

    def from_dict(self,data):
        object_assign(self,data)

    def __str__(self):
        return 'signal:{} mac:{}'.format(self.signal,self.mac)

class MessageWifiExtension(MessageBase):
    """wifi定位包
    460	1	9649	28657	23.1067600250244	114.416069030762	广东省惠州市惠城区江北街道水北
    """
    Type = PacketType.WifiLocation

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
        self.wifi_num = 0   # wifi数量
        self.wifi_data= []

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


    @staticmethod
    def unmarshall(bytes,extra=None):
        buf = ByteBuf(bytes)
        msg = MessageWifiExtension()
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
        msg.wifi_num = buf.read_uint8()
        for n in range(msg.wifi_num):
            wd = WifiData()

            mac = buf.read_bytes(6)
            wd.mac = tool_format_wifi_mac(mac)
            wd.signal = buf.read_uint8()
            msg.wifi_data.append(wd.dict())
            # print str(wd)
        return msg

    # def dict(self):
    #     # data = self.simple_info.dict()
    #     data = {}
    #     data.update(hash_object(self, excludes=('wifi_data',)))
    #
    #     return data
    #
    # def from_dict(self, data):
    #     object_assign(self, data)
    #     # self.simple_info = DeviceSimpleInfo()
    #     # object_assign(self.simple_info,data)


class MessageAudioData(MessageBase):
    Type = PacketType.AudioData
    def __init__(self):
        MessageBase.__init__(self)
        self.type = 0 # 0:录音文件 , 1: sos录音 , 2:对讲录音, 3: 指令录音
        self.check = 0 # 0:crc , 1: md5
        self.offset = 0 # 数据偏移
        self.content = ''
        self.flag = ''  #标识位，变长
        self.ymdhms = ''
        self.sequence = 0
        self.total_size = 0

    def response(self):
        """回复心跳消息包序列化数据"""
        netpack = self.extra
        netpack.set_payload('')
        return netpack.to_bytes()

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


    @staticmethod
    def unmarshall(bytes, extra=None):
        buf = ByteBuf(bytes)
        msg = MessageAudioData()
        msg.type = buf.read_uint8() # 文件类型
        msg.total_size = buf.read_uint32() #文件总长
        msg.check = buf.read_uint8()
        check_data = ''
        if msg.check == 0: # crc16
            check_data = buf.read_uint16()
        if msg.check == 1: # md5
            check_data = buf.read_bytes(16)
        msg.offset = buf.read_uint32()
        size = buf.read_uint16()
        msg.content = buf.read_bytes(size)
        if msg.type in (0,2): # 录音文件s
            # msg.flag = buf.read_bytes(6)
            # y = 2000 + buf.read_uint8()
            # m = buf.read_uint8()
            # d = buf.read_uint8()
            # h = buf.read_uint8()
            # M = buf.read_uint8()
            # s = buf.read_uint8()
            # msg.ymdhms = '{}{:02d}{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, h, M, s)
            msg.parse_time(buf)
            
        elif msg.type == 1: #对应 SOS、声控 报警包序列号相同
            msg.flag = buf.read_uint16()
        elif msg.type == 3:
            msg.flag = buf.read_uint32()
            msg.sequence = buf.read_uint16()
        return msg

    def dict(self):
        data = {}
        data.update(hash_object(self,excludes=('content',)))
        return data

    def from_dict(self, data):
        pass


def tool_format_wifi_mac(bytes):
    value = ':'.join(map(lambda _:'%02x'%_,map(ord,bytes) ))
    return value



def registerMessageObject(msgcls):
    MessageClsDict[msgcls.Type.value] = msgcls

# print globals().keys()
for key,value in locals().items():
    if key.find('Message')==0 and key not in ('MessageClsDict','MessageBase'):
        registerMessageObject(value)

# print MessageClsDict.values()
