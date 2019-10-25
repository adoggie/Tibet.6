#coding:utf-8

class BoxControllerInfo(object):
    def __init__(self):
        self.name = ''
        self.mac = ''
        self.device_id = ''
        self.vendor = ''
        self.category = ''
        self.desc = ''
        self.probe_list=[]

class ProbeDeviceInfo(object):
    """探测设备信息"""
    def __init__(self):
        self.name=''
        self.mac = ''
        self.device_id   = ''
        self.vendor=''
        self.category=''
        self.desc=''