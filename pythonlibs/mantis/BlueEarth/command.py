#coding:utf-8

from mantis.fundamental.utils.useful import hash_object

class ServerInfo(object):
    IP = 'ip'
    DOMAIN = 'domain'
    def __init__(self):
        self.address = ''   # ip or domain
        self.type  = ServerInfo.IP      # 1 : ip , 2: domain
        self.port = 0

    def parse(self,*args):
        """传入的多个参数解析
            type, address,port
        """
        try:
            self.type = args[0].lower()
            self.address = args[1]
            self.port = args[2]
        except:pass

        return self

class SosInfo(object):
    def __init__(self):
        self.sos_1 = ''
        self.sos_2 = ''
        self.sos_3 = ''

    def parse(self, *args):
        """传入的多个参数解析
            sos1,sos2,sos3
        """
        try:
            self.sos_1 = args[0]
            self.sos_2 = args[1]
            self.sos_3 = args[2]
        except:
            pass
        return self


class PositionMode(object):
    TIMING = 'timing'   # 定时
    SMART = 'smart'     # 智能触发

    def __init__(self):
        self.mode_current = PositionMode.SMART
        self.mode_timing = 0    # 定时上传间隔
        self.mode_smart = 0     # 智能模式上传间隔

    def parse(self,*args):
        """
        mode,value
        """
        try:
            self.mode_current = args[0]
            if self.mode_current == PositionMode.TIMING:
                self.mode_timing = args[1]
            if self.mode_current == PositionMode.SMART:
                self.mode_smart = args[1]

        except:pass
        return self


class FenceInfo(object):
    CIRCLE = 'circle'
    RECT = 'rect'
    def __init__(self):
        self.index = 0
        self.type = 'circle'  # circle or rect
        self.radius = 0         # 半径
        self.width = 0          # 矩形宽度
        self.height = 0         # 矩形高度
        self.lon = 0            # 经度
        self.lat = 0            # 纬度

    def parse(self, *args):
        """传入的多个参数解析
            index,type,lon,lat,radius
            index,type,lon,lat,width,height
        """
        try:
            self.index = args[0]
            self.type = args[1].lower()
            self.lon = args[2]
            self.lat = args[3]
            if self.type == FenceInfo.CIRCLE:
                self.radius = args[4]
            if self.type == FenceInfo.RECT:
                self.width = args[4]
                self.height = args[5]

        except:
            pass
        return self

class VersionInfo(object):
    def __init__(self):
        self.version = ''

class StatusInfo(object):
    def __init__(self):
        self.battery = 0
        self.gsm = 0



COMMAND_MAGIC = '$'  # 标识这是个命令包，否则为设备的原始控制包

FENCE_IN = 'IN'
FENCE_OUT = 'OUT'

"""
两种命令处理方式: 
1. 设备原生命令 , 例如: SOS#, VERSION# ,...
2. 标准设备控制命令, 
例如:  
    $set-sos,13916624477,18601636346   $set-sos 将被映射到 方法: .setSos()
    $get-version  映射到 .getVersion()
"""
class CommandBaseController(object):
    def __init__(self):
        pass

    def execute(self,data):
        """解析获得设备的执行命令"""
        data = data.strip()
        if not data:
            return ''
        if data.find(COMMAND_MAGIC) != 0 : # 结构化的命令
            return data
        data = data[1:]
        # 扫描本类成员函数是否是对应的命令
        attrs = [s for s in dir(self) if not s.startswith('__')]
        fields = map(lambda _: _.strip(),data.split(','))

        command = fields[0].lower().replace('-','')
        params = fields[1:]

        func = None
        for k in attrs:
            if k.lower() == command:
                func = getattr(self,k)
                break
        data=''
        if func:
            data = func(*params)   # 将参数作为变参传入不同的命令处理函数
        return data


    def positionNow(self):
        """立即定位
            $position-now
        """
        raise NotImplementedError

    def positionNowGps(self):
        raise NotImplementedError

    def positionNowLbs(self):
        raise NotImplementedError

    def positionNowWifi(self):
        raise NotImplementedError

    def getParameters(self):
        raise  NotImplementedError

    def getVersion(self):
        """ $get-version"""
        raise NotImplementedError

    def getStatus(self):
        """ $get-status"""
        raise NotImplementedError

    def getPositionUrl(self):
        """返回定位的url链接
            $get-position-url
        """
        raise NotImplementedError

    def getSos(self):
        """返回紧急联系人设置, 多个联系电话
            $get-sos
        """
        raise NotImplementedError

    def setSos(self,*args):
        """设置指定位置的紧急联系人电话
            $set-sos,1,2,3,4
        """
        # sos = SosInfo()
        # sos.parse(*args)
        # return sos
        raise  NotImplementedError

    def clearSos(self,tel):
        """删除sos电话"""
        raise NotImplementedError


    def getServer(self):
        """查询服务器配置
            $get-server
        """
        #
        raise  NotImplementedError


    # def setServer(self,*args):
    #     """设置服务器信息
    #         $set-server,...
    #     """
    #     server = ServerInfo()
    #     server.parse(*args)
    #     return server
    #     # 给子类直接使用解析的参数

    def setIpServer(self,address,port):
        return NotImplementedError

    def setDomainServer(self,address,port):
        return NotImplementedError

    def getPositionMode(self):
        """查询定位模式
            $get-position-mode
        """
        return ''

    def setPositionModeTiming(self):
        """设置定位模式
            $set-position-mode-timing
        """
        raise NotImplementedError

    def setPositionModeSmart(self):
        raise NotImplementedError

    def setPositionModeTimingValue(self,value):
        return ''

    def setPositionModeSmartValue(self,value):
        return ''

    def getFence(self):
        """查询围栏信息"""
        raise NotImplementedError

    def setCircleFence(self,lon,lat,radius,inout):
        """设置围栏"""
        raise NotImplementedError

    def setRectFence(self,lon,lat,width,height,inout):
        raise  NotImplementedError

    # def deleteFence(self,index):
    #     """ index : -1 所有围栏"""
    #     raise NotImplementedError

    def enableFenceAlarm(self):
        """允许围栏报警"""
        return ''

    def disableFenceAlarm(self):
        """禁用围栏报警"""
        return ''


    def getSpeedAlarm(self):
        return ''

    def enableSpeedAlarm(self):
        return ''

    def disableSpeedAlarm(self):
        return ''

    def getBatteryAlarm(self):
        return ''

    def enableBatteryAlarm(self):
        return ''

    def disableBatteryAlarm(self):
        return ''

    def getSosAlarm(self):
        return ''

    def enableSosAlarm(self,*args):
        return ''

    def disableSosAlarm(self):
        return ''

    def reset(self):
        return ''

    def shutdown(self):
        return ''

    def getHeartBeat(self):
        return ''

    def setHeartBeat(self,value):
        return ''

    def start_audio_record(self,duration=10):
        return ''

    def start_audio_listen(self):
        """启动录音"""
        return ''

    def setListenMode(self,yes=True):
        """启用侦听模式
        拨打电话到设备，设备默认是双向通话模式 yes = false,
        监听两种模式：
            1. sos手机拨打设备
            2. 设备主动拨打sos手机 ( 必须sos手机发送jt指令给设备）
        如果要实现手机拨打设备电话，设备自动进入监听模式 yes = true
        """
        return ''

    def getListenMode(self):
        """查询当前设备监听模式"""
        return ''


    def init_commands(self):
        cmds =(self.getVersion(),
               self.getParameters(),
               self.getServer(),
               self.getFence(),
               self.getHeartBeat(),
               self.getStatus()
               )
        return cmds