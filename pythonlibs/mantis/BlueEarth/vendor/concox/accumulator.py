#coding:utf-8

from protocal import *
from packet import NetWorkPacket
import message

class DataAccumulator(object):
    def __init__(self):
        self.buff = ''
        self.cfgs = None

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
            index = self.buff.find(NetWorkPacket.END_FLAG)
            if index == -1:
                break # cant get a whole packet

            packet = NetWorkPacket()
            data = self.buff[:index+len(NetWorkPacket.END_FLAG)]
            self.buff = self.buff[len(data):]  # remain buff
            msg = packet.unpack(data)
            if msg:
                messages.append(msg)
        return messages



MessageClsDict ={}



