#coding: utf-8

from mantis.fundamental.errors import ErrorEntry

class ErrorDefs(object):
    OK                  = ErrorEntry(0,u'succ')
    Error               = ErrorEntry(1,u'未定义的错误')
    SystemFault         = ErrorEntry(9001, u'系统故障')
    ObjectNotExist      = ErrorEntry(10001,u'对象不存在')
    AccessDenied        = ErrorEntry(10002,u'权限受限')
    PermissionInsufficient = ErrorEntry(10003,u'权限不够')
    ParameterInvalid    = ErrorEntry(10004,u'参数无效')
    PasswordError       = ErrorEntry(10005,u'密码错误')
    TargetIsOffline     = ErrorEntry(10006,u'设备离线')
    TargetIsBusy        = ErrorEntry(10007,u'设备繁忙中')
    TokenIsDirty        = ErrorEntry(10008,u'无效的令牌')
    UserNotExist        = ErrorEntry(10009,u'用户不存在')
    ObjectHasExist        = ErrorEntry(10010,u'对象已存在')
    NeedPassword        = ErrorEntry(20001,u'需要提供密码')
    ResExpired        = ErrorEntry(20002,u'资源已过期')
    ReachLimit        = ErrorEntry(20003,u'达到上限')



