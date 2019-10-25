#coding:utf-8

import struct

# pip install CRC-ITU
def get_crc_16(data):
    from crc_itu import crc16
    # print(hex(crc16(b'your bytes')))
    return crc16(data)


class ByteBuf(object):
    def __init__(self,bytes=''):
        self.bytes = bytes
        self.index =0
        self.save_index=0

    def read_bytes(self,n):
        bytes = self.bytes[self.index:self.index+n]
        self.index+=n
        return bytes

    def read_uint16(self):
        value, = struct.unpack('!H', self.bytes[self.index:self.index + 2])
        self.index+=2
        return value

    def read_uint32(self):
        value, = struct.unpack('!I', self.bytes[self.index:self.index + 4])
        self.index+=4
        return value

    def read_uint8(self):
        value, = struct.unpack('B',self.bytes[self.index])
        self.index += 1
        return value

    def save(self):
        self.save_index = self.index

    def restore(self):
        self.index = self.save_index

    def forward(self,n):
        self.index+=n

    def back(self,n):
        self.index -= n

    def move(self,n):
        self.index = n

    def position(self):
        return self.index

    def write_bytes(self,bytes):
        self.bytes+=bytes

    def write_uint16(self,value):
        self.bytes += struct.pack('!H',value)

    def write_uint32(self, value):
        self.bytes += struct.pack('!I', value)

    def write_uint8(self,value):
        self.bytes += struct.pack('B',value)

    def size(self):
        return len(self.bytes)

