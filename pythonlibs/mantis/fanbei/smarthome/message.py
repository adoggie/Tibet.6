#coding:utf-8

from mantis.fundamental.utils.useful import hash_object,object_assign

from mantis.fundamental.network.message import JsonMessage
from mantis.fanbei.smarthome.base import *

"""

"""


# class MessageGetServerTime(Message):
#     """获取系统时钟"""
#
#     def __init__(self):
#         Message.__init__(self)
#         pass
#
#
# class MessageInitParamReq(Message):
#     def __init__(self):
#         Message.__init__(self, 'initparam_req')
#         self.dev_id = ''  # 设备编号
#         self.dev_type = ''  # 设备类型
#         self.version = ''  # 系统版本
#         self.time = ''  # 当前时间
#         self.signature = ''  # 数据签名


class MessageTraverse(JsonMessage):
    OFFSET_BID = 0  #
    OFFSET_DOWN = 1
    OFFSET_UP = 2
    NAME = ''

    def __init__(self, name):
        JsonMessage.__init__(self, name)
        self.device_id = ''
        # self.id = ''
        # self.name = name
        # self.values = {}
        # self.extras = {'time': '', 'ver': ''}  #
        # self.offset = self.OFFSET_BID

        # self.mod = ModuleType.Primary
    def values(self):
        return hash_object(self,excludes=('id_','name_','values_','extras_','NAME','OFFSET_BID','OFFSET_DOWN','OFFSET_UP'))

    # def dict(self):
    #     data = dict(id=self.id, name=self.name, values=self.values, extras=self.extras, offset=self.offset)
    #     return data
    #
    # def json(self):
    #     return json.dumps(self.dict())

    # def values(self):
    #     return dict(device_id=self.device_id)


class MessageTraverseDown(MessageTraverse):
    """下行消息"""

    def __init__(self, name):
        MessageTraverse.__init__(self, name)
        # self.offset = self.OFFSET_DOWN



class MessageTraverseUp(MessageTraverse):
    """上行消息"""

    def __init__(self, name):
        MessageTraverse.__init__(self, name)
        # self.offset = self.OFFSET_UP


class MessageLogin(MessageTraverseUp):
    """设备登陆请求"""
    NAME = 'login'

    def __init__(self):
        MessageTraverseUp.__init__(self, self.NAME)
        self.token = ''

    # def values(self):
    #     data = MessageTraverse.values(self)
    #     data['token'] = self.token
    #     return data


class MessageLoginResp(MessageTraverseDown):
    """设备登陆反馈消息"""
    NAME = 'login_resp'

    def __init__(self):
        MessageTraverseDown.__init__(self, self.NAME)
        self.error = 0  # 错误码 0 : 成功
        self.message = ''
        self.server_time = 0


class MessageHeartBeat(MessageTraverse):
    """设备与平台之间的心跳消息"""
    NAME = 'heartbeat'

    def __init__(self):
        MessageTraverse.__init__(self, self.NAME)


class MessageDeviceStatusQuery(MessageTraverseDown):
    """平台下发设备状态查询请求"""
    NAME = 'dev_status_query'

    def __init__(self):
        MessageTraverseDown.__init__(self, self.NAME)

class MessageDeviceStatus(MessageTraverseUp):
    NAME = 'dev_status'
    def __init__(self):
        MessageTraverseUp.__init__(self, self.NAME)
        # self.host_ver = ''  # 版本
        # self.mcu_ver = ''
        # self.status_time = 0      # 主机时间
        # self.boot_time = 0     # 设备启动时间
        self.params = {}  # 指定特定功能的运行参数


    # def values(self):
    #     data = {}
    #     data.update(hash_object(self.host,key_prefix='host_'))
    #     data.update(hash_object(self.mcu,key_prefix='mcu_'))
    #     return data

class MessageDeviceValueSet(MessageTraverseDown):
    """设备运行参数设置"""
    NAME = 'dev_val_set'

    def __init__(self):
        MessageTraverseDown.__init__(self, self.NAME)
        self.mod_type = ModuleType.First  # 主设备
        self.param_name = ''  #
        self.param_value = ''


class MessageSensorStatusQuery(MessageTraverseUp):
    """查询指定传感器模块运行参数"""
    NAME = 'sensor_status_query'

    def __init__(self):
        MessageTraverseUp.__init__(self, self.NAME)
        self.sensor_type = SensorType.All
        self.sensor_id = Constants.Undefined


class MessageSensorStatus(MessageTraverseUp):
    """上传传感器模块运行参数"""
    NAME = 'sensor_status'

    def __init__(self):
        MessageTraverseUp.__init__(self, self.NAME)
        self.sensor_type = SensorType.Undefined
        self.sensor_id = Constants.Undefined
        self.params = {}  # 指定特定功能的运行参数


class MessageSensorValueSet(MessageTraverseDown):
    """下发对传感器的控制"""
    NAME = 'sensor_val_set'

    def __init__(self):
        MessageTraverseDown.__init__(self, self.NAME)
        self.sensor_type = SensorType.Undefined
        self.sensor_id = Constants.Undefined
        self.param_name = ''
        self.param_value = ''

# class MessageIoTSensorValueSet(MessageSensorValueSet):
#     name = 'iot_sensor_val_set'
#     def __init__(self):
#         MessageSensorValueSet.__init__(self,self.NAME)
#         self.device_id = ''     # smartbox 硬件编号

class MessageDeviceCommand(MessageTraverseDown):
    """平台下发设备控制命令"""
    NAME = 'dev_command'
    def __init__(self):
        MessageTraverseDown.__init__(self, self.NAME)
        self.mod_type = ModuleType.Primary  # 默认主机
        self.command = ''  # 待更新的版本
        self.params  = {}  # 命令参数


class MessageDeviceUpgrade(MessageTraverseDown):
    """平台下发设备升级请求"""
    NAME = 'dev_upgrade'

    def __init__(self):
        MessageTraverseDown.__init__(self, self.NAME)
        self.mod_type = ModuleType.Primary  # 默认主机
        self.ver = ''  # 待更新的版本
        self.md5 = ''  # 散列值
        self.access_code = ''  # 访问身份码
        self.server_url = ''  # 更新服务器地址


class MessageDeviceLogInfo(MessageTraverseUp):
    """设备运行日志上报"""
    NAME = 'dev_log'

    def __init__(self):
        MessageTraverseUp.__init__(self, self.NAME)
        # self.mod_type = ModuleType.Primary
        self.time = 0  # 日志时间
        self.level = ''
        self.content = ''  # 日志内容


MessageClsDict ={}

def registerMessageObject(msgcls):
    MessageClsDict[msgcls.NAME] = msgcls


for key,value in locals().items():
    if key.find('Message')==0 and key not in ('MessageClsDict','Message','MessageType','MessageSplitter'):
        registerMessageObject(value)

def parseMessage(data):
    print data
    if  isinstance(data,str):
        data = json.loads(data)

    message = data.get('name')
    msgcls = MessageClsDict.get(message)
    if not msgcls:
        print 'Message Type unKnown. value:{}'.format(message)
        return None
    data = data.get('values',{})
    msg = msgcls()
    msg.assign(data)
    return msg

if __name__=='__main__':
    data='''{
        "id": "",
        "name": "sensor_status",
        "values": {
            "params": {
                "1": "0"
            },
            "sensor_id": 1,
            "sensor_type": 1
        }
    }'''
    m = parseMessage(data)
    print m.id
