#coding:utf-8

from protocal import *
from packet import NetWorkPacket
import message

class DataAccumulator(object):
    def __init__(self,packet_cls=NetWorkPacket):
        self.buff = ''
        self.cfgs = None
        self.packet_cls = packet_cls

    def init(self,cfgs):
        self.cfgs = cfgs
        return self

    def open(self):
        pass

    def close(self):
        pass

    def enqueue(self,bytes):
        self.buff+=bytes
        messages = [ ]
        while True:
            index = self.buff.find(NetWorkPacket.START_FLAG_1)
            if index ==-1:
                index = self.buff.find(NetWorkPacket.START_FLAG_2)
                if index == -1:
                    self.buff = ''
                    break
            self.buff = self.buff[index:]
            # index = self.buff.find(NetWorkPacket.END_FLAG) # 数据包体也会存在 0d 0a 的情况
            # if index == -1:
            #     break # need more data  eat in.

            packet = self.packet_cls()
            # data = self.buff[:index+len(NetWorkPacket.END_FLAG)]
            # 这里已经获得一个完整的包数据，包括 START_FLAG ...  END_FLAG 
            # ( 但这中处理方式过于简单，未考虑数据体内存在 END_FLAG的情况)
            # data = self.buff
            if len(self.buff) <= 4 :
                break # need more

            size = packet.check_size(self.buff)
            if len(self.buff) < size:
                break # need more

            data = self.buff[:size]
            self.buff = self.buff[size:]  # remain buff

            if data[-2:] != NetWorkPacket.END_FLAG: # 终止标志不对
                break

            msg = packet.unpack(data)
            if msg:
                messages.append(msg)
        return messages



MessageClsDict ={}



