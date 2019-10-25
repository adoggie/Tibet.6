#coding:utf-8

from mantis.fundamental.utils.useful import singleton
from protocal import PacketType,MessageClsDict

from utils import get_crc_16,ByteBuf

class NetWorkPacket(object):
    """原始数据包"""
    START_FLAG_1 = 'xx'
    START_FLAG_2 = 'yy'
    END_FLAG = '\r\n'

    def __init__(self):
        self.start_flag = self.START_FLAG_1
        self.size = 0
        self.type = 0
        self.payload = ''
        self.sequence = 0
        self.crc16 = 0
        self.stop_flag = self.END_FLAG

        self.fieldsize_width = 1

        # self.bytes = ''


    def unpack(self,bytes):
        index = 0
        buf = ByteBuf(bytes)
        self.start_flag = buf.read_bytes(2)

        if self.start_flag == self.START_FLAG_1:
            self.fieldsize_width = 1
            self.size = buf.read_uint8()
        if self.start_flag == self.START_FLAG_2:
            self.fieldsize_width = 2
            self.size  = buf.read_uint16()
        self.type = buf.read_uint8()
        if len(bytes) - 4 - self.fieldsize_width  != self.size:
            print 'Packet Size Error. '
            return None

        buf.save()
        buf.move(len(bytes)-6)
        self.sequence = buf.read_uint16()
        self.crc16 = buf.read_uint16()
        buf.restore()

        crc = self.calc_crc(bytes[2:len(bytes)-4])
        if crc != self.crc16:
            print 'Packet Crc Error.'
            return None

        msgcls = MessageClsDict.get(self.type)
        if not msgcls:
            print 'Message Type unKnown. value:{}'.format(self.type)
            return None

        payload = buf.read_bytes(self.size)
        msg = msgcls.unmarshall(payload,self)
        # msg = msgcls.unmarshall(bytes[2+self.fieldsize_width+1, len(bytes)-6])
        if not msg:
            print 'Message unmarshall Error. ',str(msgcls)
            return None
        return msg


    def calc_crc(self,bytes):
        return  get_crc_16(bytes)


    def pack(self,message):
        pass

    def get_bytes(self):
        return self.to_bytes()

    def to_bytes(self):
        buf = ByteBuf()
        self.size = 5 + len(self.payload)
        buf.write_bytes(self.start_flag)
        if self.fieldsize_width == 1:
            buf.write_uint8(self.size)
        if self.fieldsize_width == 2:
            buf.write_uint16(self.size)
        buf.write_uint8(self.type)
        buf.write_bytes(self.payload)
        buf.write_uint16(self.sequence)
        crc = self.calc_crc( buf.bytes[2:])
        buf.write_uint16(crc)
        buf.write_bytes(self.stop_flag)
        return buf.bytes

    def set_payload(self,data):
        self.payload = data

    # def size(self):
    #     """整个数据包大小"""
    #     return 0

#

@singleton
class NetWorkPacketAllocator(object):
    """网络包对象生成器，自动填充 信息序列号"""
    def __init__(self):
        self.seq_gen = None

    def setSequenceGenerator(self,generator):
        """信息序列号生成器"""
        self.seq_gen = generator
        return  self

    def createPacket(self):
        packet = NetWorkPacket()
        packet.sequence = self.seq_gen.next()
        return packet



