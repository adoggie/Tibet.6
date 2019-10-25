#coding: utf-8

from mantis.fundamental.errors import ErrorEntry

class ErrorDefs(object):
    OK                  = ErrorEntry(0,u'succ')
    Error               = ErrorEntry(1,u'未定义的错误')
    ParameterInvalid    = ErrorEntry(101,u'参数无效')
    BAR_SCALE_INVALID   = ErrorEntry(1001,u'k线时间刻度规格错误')
