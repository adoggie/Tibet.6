#coding:utf-8
import json

class MessageJsonStreamCodec(object):
    def __init__(self):
        self.max_packet_size = 1024 * 10
        self.buff = ''

    def encode(self,data):
        msg = data
        if isinstance(data,dict):
            msg = json.dumps(data)
        msg+='\0'

    def decode(self,data):
        self.buff =  self.buff + data
        result=[]
        while True:
            end = self.buff.find('\0')
            if end == -1:
                break
            p = self.buff[:end]
            try:
                obj = json.loads(p)
                result.append(obj)
            except:
                print 'invalid json data:',p
                pass
            self.buff=self.buff[end+1:]
        return result

    def reset(self):
        self.buff =''


