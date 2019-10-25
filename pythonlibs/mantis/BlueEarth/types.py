#coding:utf-8

class PositionSource(object):
    """位置数据来源"""
    EMPTY = 0
    GPS  = 1
    LBS  = 2
    WIFI = 3

class AlarmSourceType(object):
    EMPTY = ''
    GPS_ALARM = 'gps'
    LBS_ALARM = 'lbs'

class CoordinateType(object):
    """坐标类型"""
    EMPTY = 0
    WGS84 = 1
    BD = 2
    GD = 3
    TX = 4

class FenceType(object):

    CIRCLE = 'circle'
    RECT = 'rect'
    ALL = (CIRCLE,RECT)