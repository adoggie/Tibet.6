#coding:utf-8


class TypeValue(object):
    def __init__(self,value,comment=''):
        self.value = value
        self.comment = comment

class PacketType(object):
    Login       = TypeValue(0x01,u'登录包')
    GpsLocation = TypeValue(0x22,u'GPS 定位包(UTC)')
    HeartBeat   = TypeValue(0x13,u'心跳包')
    DeviceRespOnlineCN   = TypeValue(0x21,u'终端在线指令回复(中英文)')
    DeviceRespOnlineEN   = TypeValue(0x15,u'终端在线指令回复(英文)')
    AlarmData   = TypeValue(0x26,u'报警数据(UTC)')
    FenceAlarm  = TypeValue(0x27,u'多围栏设备报警数据(UTC)')
    LbsAlarm    = TypeValue(0x19,u'LBS 报警包')
    GpsAddressReq    = TypeValue(0x2A,u'GPS 地址请求包(UTC)')
    LbsAddressReq    = TypeValue(0x17,u'LBS 地址请求包')
    OnlineCommand    = TypeValue(0x80,u'在线指令')
    AdjustTime    = TypeValue(0x8A,u'校时包')
    GenericMessage    = TypeValue(0x94,u'信息传输通用包')
    AddressCNResp    = TypeValue(0x17,u'中文地址回复包')
    AddressENResp    = TypeValue(0x97,u'英文地址回复包')
    SerialUpStream    = TypeValue(0x30,u'串口透传包')
    SerialDownStream    = TypeValue(0x31,u'串口透传服务器下发')

# START_FLAG_1 = 'xx'
# START_FLAG_2 = 'yy'
# END_FLAG = '\r\n'
#


MessageClsDict ={}



