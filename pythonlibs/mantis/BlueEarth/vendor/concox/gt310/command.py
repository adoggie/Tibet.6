#coding:utf-8

from datetime import datetime
import struct
from protocal import PacketType,TypeValue
from utils import ByteBuf
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.BlueEarth.vendor.concox.ev25.command import CommandController as _CommandController


class CommandController(_CommandController):
    """命令控制器"""
    def __init__(self):
        _CommandController.__init__(self)

    def start_audio_listen(self):
        return 'JT#'

    def start_audio_record(self,duration=10):
        return 'LY,10#'

    def setListenMode(self,yes=True):
        """启用侦听模式
        拨打电话到设备，设备默认是双向通话模式 yes = false,
        监听两种模式：
            1. sos手机拨打设备
            2. 设备主动拨打sos手机 ( 必须sos手机发送jt指令给设备）
        如果要实现手机拨打设备电话，设备自动进入监听模式 yes = true
        """
        if yes:
            return 'JC,1#'  # 监听模式
        return 'JC,0#'      # 双向通话

    def getListenMode(self):
        """查询当前设备监听模式"""
        return 'JC#'