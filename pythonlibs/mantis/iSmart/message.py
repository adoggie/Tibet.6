#coding:utf-8

from mantis.fundamental.utils.useful import hash_object,object_assign

class MessageType(object):
    UP_ENDPOINT_REGISTER = 'UP_ENDPOINT_REGISTER'
    UP_ENDPOINT_STATUS_REPORT='UP_ENDPOINT_STATUS_REPORT'
    UP_ENDPOINT_ALARM = 'UP_ENDPOINT_ALARM'
    UP_ENDPOINT_HEARTBEAT = ' UP_ENDPOINT_HEARTBEAT'
    DOWN_ENDPOINT_QUERY_STATUS = 'DOWN_ENDPOINT_QUERY_STATUS'
    DOWN_ENDPOINT_CONTROL = 'DOWN_ENDPOINT_CONTROL'
    UP_BOX_REGISTER = 'UP_BOX_REGISTER'



class MessageObject(object):
    message = ''
    def __init__(self):
        self.params={}

    def dict(self):
        return hash_object(self)

    def from_dict(self, data):
        object_assign(self,data)

class MessageHeartbeat(MessageObject):
    message = MessageType.UP_ENDPOINT_HEARTBEAT
    def __init__(self):
        MessageObject.__init__(self)

class MessageEndpointRegister(MessageObject):
    message = MessageType.UP_ENDPOINT_REGISTER
    def __init__(self):
        MessageObject.__init__(self)
        self.device = None

    def dict(self):
        data = hash_object(self,excludes=('message',))
        data.update( hash_object(self.device))
        return data

class MessageEndpointStatus(MessageObject):
    message = MessageType.UP_ENDPOINT_STATUS_REPORT
    """设备状态信息在 params{} 携带"""
    def __init__(self):
        MessageObject.__init__(self)

        self.status = {}

class MessageEndpointAlarm(MessageObject):
    message = MessageType.UP_ENDPOINT_ALARM
    def __init__(self):
        MessageObject.__init__(self)

        self.alarm = {}

class MessageBoxRegister(MessageObject):
    message = MessageType.UP_BOX_REGISTER
    def __init__(self):
        MessageObject.__init__(self)
        self.box = None

MessageClsDict ={}

def registerMessageObject(msgcls):
    MessageClsDict[msgcls.Type.value] = msgcls


for key,value in locals().items():
    if key.find('Message')==0 and key not in ('MessageClsDict','MessageBase','MessageType'):
        registerMessageObject(value)

def parseMessage(data):
    if not isinstance(data,dict):
        return None

    message = data.get('message')
    msgcls = MessageClsDict.get(message)
    if not msgcls:
        print 'Message Type unKnown. value:{}'.format(message)
        return None
    msg = msgcls()
    msg.from_dict(data)
    return msg
