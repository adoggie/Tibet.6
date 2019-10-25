# coding:utf-8

import traceback
import json
from collections import OrderedDict



class Message(object):
    def __init__(self, name='', data={},head={}):
        self.name       = name
        self.data       = data
        self.head     = head

    def marshall(self):
        message = OrderedDict(name = self.name,
                              head = self.head,
                              data = self.data
                              )
        return json.dumps(message)

    @staticmethod
    def unmarshall(data):
        try:
            if not isinstance(data,dict):
                data = json.loads(data)

            msg = None

            msg = Message()
            msg.name = data.get('name','')
            msg.data = data.get('data',{})
            msg.head = data.get('head',{})
        except:
            traceback.print_exc()
            print 'Exception Data:',data
            msg = None
        return msg

    def __str__(self):
        return 'Name:{}\nHead:{}\nData:{}'.format(self.name,self.head,self.data)

class Request(object):
    def __init__(self, channel,back_url=''):
        self.channel = channel
        self.back_url = back_url

    def send(self,message):
        if isinstance(message,Message):
            if self.back_url:
                message.head['back_url'] = self.back_url
            self.channel.publish_or_produce(message.marshall())
        else:
            self.channel.publish_or_produce(message)

