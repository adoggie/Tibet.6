#coding: utf-8

from mantis.fundamental.errors import ErrorEntry

class ErrorDefs(object):
    NoError                  = ErrorEntry(0,u'no error')
    UnknownError               = ErrorEntry(1,u'未定义的错误')

    SystemFault         = ErrorEntry(1001, u'系统故障')
    TokenInvalid      = ErrorEntry(1002,u'令牌错误')
    AccessDenied        = ErrorEntry(1003,u'访问受限')
    PermissionDenied = ErrorEntry(1004,u'权限受限')
    ParameterInvalid    = ErrorEntry(105,u'参数无效')

    PasswordError       = ErrorEntry(1006,u'密码错误')
    UserNotExist     = ErrorEntry(1007,u'用户不存在')
    ObjectHasExist        = ErrorEntry(1008,u'对象已存在')
    ObjectNotExist        = ErrorEntry(1009,u'对象不存在')
    ResExpired        = ErrorEntry(1010,u'资源过期')
    ReachLimit        = ErrorEntry(1011,u'达到上限')

    DeviceServerNotFound        = ErrorEntry(2001,u'接入服务器未配置')
    DeviceNotOnline        = ErrorEntry(2002,u'设备未在线')






