#coding:utf-8

from datetime import datetime
import struct
from protocal import PacketType,TypeValue
from utils import ByteBuf
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.BlueEarth.command import CommandBaseController

"""
Online Command 
"""

class CommandBase(object):
    def __init__(self,query_s,set_s=''):
        self.extra = None
        self.name = ''
        self.query_s = ''
        self.set_s  =''

    def query_string(self,*args):
        if args:
            return self.query_s.format(*args)
        return self.query_s

    def set_string(self,*args):
        if args:
            return self.set_s.format(*args)
        return self.set_s


VERSION = CommandBase('VERSION#')     # 版本查询
PARAM   = CommandBase('PARAM#')         # 查询参数设置
SCXSZ   = CommandBase('SCXSZ#')         # 精简参数查询
GPRSSET = CommandBase('GPRSSET#')       # 查询 GPRS 参数
STATUS  = CommandBase('STATUS#')         # 查询状态
WHERE  = CommandBase('WHERE#')         # 经纬度位置查询指令
URL  = CommandBase('URL#')         # 位置链接查询指令
DW  = CommandBase('DW')         # 地址查询
POSITION  = CommandBase('POSITION')         # 地址查询
_123  = CommandBase('123')         # 地址查询

ASETAPN = CommandBase('ASETAPN#','ASETAPN,{}#') # X=ON/OFF；ON：开启APN自适应，OFF：关闭APN自适应
ASETGMT = CommandBase('ASETGMT#','ASETGMT,{}#') # X=ON/OFF；ON：开启时区自适应，OFF：关闭时区自适应

# SERVER,1,<域名>,<端口>[,0]#
#  SERVER,0,<IP>,<端口>[,0]# 
# 第三个参数：0 TCP（默认），1 UDP
SERVER_IP = CommandBase('SERVER#','SERVER,0,{},{},0#')
SERVER_DOMAIN = CommandBase('SERVER#','SERVER,1,{},{},0#')
GMT = CommandBase('GMT#','SERVER,{},{},{}#')
FACTORY = CommandBase('FACTORY#')
LANG_CN = CommandBase('LANG#','LANG,1#')
LANG_EN = CommandBase('LANG#','LANG,0#')
RESET = CommandBase('RESET#')
SOS_ADD = CommandBase('SOS#','SOS,A,{},{},{}#')    # 添加SOS号码
SOS_DEL = CommandBase('SOS#','SOS,D,{},{},{}#')    # SOS,<D>,<号码序号 1>[,号码序号 2][,号码序号 3]#     根据序号，删除对应的SOS号码
SOS_DEL_NUMBER = CommandBase('SOS#','SOS,D,{}#')    # SOS,<D>,<电话号码>#     根据号码，全匹配，删除对应的SOS号码
HBT = CommandBase('HBT#','HBT,{}#')    #心跳包设置间隔 T=1～300分钟，心跳包上传间隔，默认值：3分钟；
ANGLEREP_OFF = CommandBase('ANGLEREP#','ANGLEREP,OFF#')    #心跳包设置间隔 T=1～300分钟，心跳包上传间隔，默认值：3分钟；

# ANGLEREP,<X>[,A][,B]#
# X=ON/OFF，默认值：OFF     A=5～180度，偏转角度；默认值：20度；
# B=2～5秒，检测时间；默认值：2秒， ANGLEREP,OFF#     关闭拐点补传 ANGLEREP#     查询拐点补传功能是否启用，对应的参数设置值
ANGLEREP = CommandBase('ANGLEREP#','ANGLEREP,ON,{},{}#')

# SENSOR,<A>[,B][,C]# 
# A=10～300秒，检测时间，默认值为：10秒     B=10～300秒，报警延时，默认值为：10秒
# C=1-3000分钟，震动报警间隔，默认5分钟
#  SENSOR#     查询已设置的参数

SENSOR = CommandBase('SENSOR#','SENSOR,{},{},{}#')

# SENSOR 控制 GPS 时间 SENDS,<A>#
# A=0-300分钟，检测到一次震动，开启 GPS 工作的时间，0表示GPS常开，默认值：2分钟
# SENDS# 查询已设置的参数

SENDS = CommandBase('SENDS#','SENDS,{}#')

# 备份数据清除指令
CLEAR = CommandBase('CLEAR#',)


GFENCE = CommandBase('GFENCE#',)
GFENCE_CIRCLE = CommandBase('GFENCE#','GFENCE,{},{},0,{},{},{},{},{}#')
GFENCE_RECT = CommandBase('GFENCE#','GFENCE,{},{},0,{},{},{},{},{},{}#')

# 低电报警
BATALM = CommandBase('BATALM#','BATALM,ON,{}#')
BATALM_OFF = CommandBase('BATALM#','BATALM,OFF#')
# SOS 报警
SOSALM = CommandBase('SOSALM#','SOSALM,ON,{}#')
SOSALM_OFF = CommandBase('SOSALM#','SOSALM,OFF#')

#电话重拨次数
CALL = CommandBase('CALL#','CALL,{}#')  # CALL,N#     N=1～3；默认值：1；针对所有电话报警

# 设置接收报警号码（除SOS报警）
# ALMREP,A,B,C#
#     A=0~1；是否允许第一个SOS号码接收报警；0，不允许，1，允许。默认值：1
#     B=0~1；是否允许第二个SOS号码接收报警；0，不允许，1，允许。默认值：1
#     C=0~1；是否允许第三个SOS号码接收报警；0，不允许，1，允许。默认值：1

ALMREP = CommandBase('ALMREP#','ALMREP,{},{},{}#')  #

# 短信转发
# FW,<A>,<B>#
# A=电话号码；发送的电话号码
# B=信息内容；转发的短信内容
FW = CommandBase('','FW,{},{}#')  #

# 查询工作模式参数
# MODE<,A><,T>#
# A=1、2；
# 1: 定时定位模式; 2：智能定位模式；3：深度休眠模式。默认模式：2；
# T=10~86400;单位：秒；默认：180（模式1）；30（模式2）；
#
# mode,3,T1,T2#
#  T1为上传时刻（HH:MM)，默认：08：00;
#  T2为间隔时间（小时）: 1~24；默认：24；

MODE = CommandBase('MODE#')  #
MODE1 = CommandBase('MODE#','MODE,1,{}#')  #
MODE2 = CommandBase('MODE#','MODE,2,{}#')  #
MODE3 = CommandBase('MODE#','MODE,3,{},{}#')  #

# 监听指令
JT = CommandBase('JT')  #
MONTOR = CommandBase('MONTOR#')  #

# ICCID号点名查询
ICCID = CommandBase('ICCID#')  #
# 查询终端SIM卡IMSI号码
IMSI = CommandBase('IMSI#')  #
# 定位方式开关
# FIXMODE,A,B#
#    A =0～1  卫星定位，0：关闭卫星定位，1：打开卫星定位；
#    B = 0～1  WIFI+LBS定位，0：关闭WIFI+LBS定位，1：打开WIFI+LBS定位；
FIXMODE = CommandBase('FIXMODE#','FIXMODE,{},{}#')  #

# 定位方式优先级设置
# FIXPRI,A#
#    A=0~1
#    0  WIFI+LBS 定位 > GPS 定位
#    1  GPS 定位 > WIFI+LBS 定位 (默认）

FIXPRI = CommandBase('FIXPRI#','FIXPRI,{}#')  #

#远程关机
SHUTDOWN = CommandBase('SHUTDOWN#','SHUTDOWN#')  #
# WIFI点名上报
WIFION = CommandBase('WIFION#','WIFION#')  #
# 立即定位
LJDW = CommandBase('LJDW#','LJDW#')  #

# LY,10# 在服务器下发这个,就是录音10秒的指令
LY = CommandBase('','LY,{}#')

GPSON = CommandBase('GPSON#','GPSON#')#  立即开启GPS搜星定位5分钟，5 分钟内20秒定位一次(经纬度数据有变化)


class CommandController(CommandBaseController):
    """命令控制器"""
    def __init__(self):
        CommandBaseController.__init__(self)

    def positionNow(self):
        return 'GPSON#LBS#'
    # LBS# 请求lbs定位上报

    def positionNowGps(self):
        return 'GPSON#'

    def positionNowLbs(self):
        return 'LBS#'

    def positionNowWifi(self):
        return ''

    def getParameters(self):
        return 'PARAM#'

    def getVersion(self):
        return 'VERSION#'

    def getStatus(self):
        return 'STATUS#'

    def getPositionUrl(self):
        return 'URL#'

    def getSos(self):
        return 'SOS#'

    def setSos(self,*args):
        """"""
        sos = 'SOS,A,' + ','.join(args) +'#'
        return sos

    def clearSos(self,tel):
        sos = 'SOS,D,'+tel+'#'
        return sos

    def getServer(self):
        return 'SERVER#'


    def setIpServer(self,address,port):
        return 'SERVER,0,{},{},0#'.format(address,port)

    def setDomainServer(self,address,port):
        return 'SERVER,1,{},{},0#'.format(address,port)


    def getPositionMode(self):
        return 'MODE#'

    def setPositionModeTiming(self):
        return 'MODE,1#'

    def setPositionModeSmart(self):
        return 'MODE,2#'

    def getFence(self):
        return 'FENCE#'

    def setCircleFence(self, lon, lat, radius,inout):
        """设置围栏"""
        return 'FENCE,,0,{lat},{lon},{meter},{inout},1#'.format(lat=lat,lon=lon,meter=radius,inout=inout)

    def setRectFence(self, lon1, lat1,lon2,lat2,inout):
        return 'FENCE,,1,{lat1},{lon1},{lat2},{lon2},{inout},1#'.\
            format(lat1=lat1, lon1=lon1, lat2=lat2,lon2=lon2, inout=inout)

    # def deleteFence(self, index):
    #     """ index : -1 所有围栏"""
    #     raise NotImplementedError

    def enableFenceAlarm(self):
        """允许围栏报警"""
        return 'FENCE,ON#'

    def disableFenceAlarm(self):
        """禁用围栏报警"""
        return 'FENCE,OFF#'

    def enableSpeedAlarm(self):
        return ''

    def disableSpeedAlarm(self):
        return ''

    def getBatteryAlarm(self):
        return 'BATALM#'

    def enableBatteryAlarm(self):
        s = 'SOSALM,ON#'
        return s

    def disableBatteryAlarm(self):
        return 'BATALM,OFF#'

    def getSosAlarm(self):
        return 'SOSALM#'

    def enableSosAlarm(self,*args):
        s = 'SOSALM,ON'
        if len(args):
            s+=','+args[0]
        s+='#'
        return s

    def disableSosAlarm(self):
        return 'SOSALM,OFF#'

    def reset(self):
        return 'RESET#'

    def shutdown(self):
        return ''

    def getHeartBeat(self):
        return 'HBT#'

    def setHeartBeat(self,value):
        return 'HBT,{}#'.format(value)

    def start_audio_listen(self):
        return 'JT#'