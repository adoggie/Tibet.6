#coding:utf-8

from camel.fundamental.errors import hash_object,ErrorEntry

class ErrorDefs:
    __ver__ =u'1.0'
    __BASE__ = 0

    SUCC = ErrorEntry(0, u'成功')

class ErrorDefsDispatcher:
    __ver__ = u'1.0'
    __BASE__ = 10000

    OK                  = ErrorEntry(1000, u'success成功')
    DB_ERROR            = ErrorEntry(1001, u'数据库错误')
    LOGIN_FAIL          = ErrorEntry(1002, u'登录失败')
    REPEAT_TIC          = ErrorEntry(1003, u'')
    SERVER_ERR          = ErrorEntry(1004, u'服务器错误')
    REFRESH             = ErrorEntry(1005, u'')
    TRANS_OK            = ErrorEntry(1006, u'')
    TRUCK_IS_ONWAY      = ErrorEntry(1007, u'车辆正在运输中')
    UNKNOW_DEVICE       = ErrorEntry(1008, u'未知设备，仅支持web登录')
    AUTH_FAIL           = ErrorEntry(1100, u'鉴权失败')
    NO_TOKEN            = ErrorEntry(1101, u'没有TOKEN')
    NO_USER             = ErrorEntry(1102, u'没有用户')
    TOKEN_INVALID       = ErrorEntry(1103, u'token已失效')
    NO_VOUCHER          = ErrorEntry(1104, u'票据获取失败')
    USER_NOT_ACTIVE     = ErrorEntry(1201, u'用户未激活')
    RESET_PWD_FAIL      = ErrorEntry(1202, u'重置密码错误')
    USER_UP_ERR         = ErrorEntry(1203, u'用户更新错误')
    USER_NO_AUTHORIZATION = ErrorEntry(1204, u'用户无权限')
    NO_DRIVER           = ErrorEntry(1300, u'司机用户不存在')
    NO_GROUP_STATUS     = ErrorEntry(1301, u'不存在此状态组')
    NO_TNUMBER          = ErrorEntry(1302, u'无此订单')
    INVALID_STATUS      = ErrorEntry(1303, u'运单状态无效')
    VALUE_ERROR         = ErrorEntry(1304, u'参数值错误')
    TRANS_DATA_CHANGED  = ErrorEntry(1305, u'运单状态被改变')
    TRANS_STATUS_CHANGE_FAIL = ErrorEntry(1306, u'运单状态改变失败')
    LOCATION_NOT_IN_TRANS = ErrorEntry(1307, u'该地点不存在运单中')
    TRANS_FINISHED      = ErrorEntry(1308, u'运单已完成，异常上报失败')
    TRANS_IS_EXIST      = ErrorEntry(1309, u'运单号已存在')
    PLATE_NO_TRANS      = ErrorEntry(1310, u'此车牌无正在进行中的运单')
    NO_LOCATION         = ErrorEntry(1401, u'没有此location编码')
    NOTE_EXIST          = ErrorEntry(1402, u'重复添加note')
    RECORD_EXIST        = ErrorEntry(1403, u'重复补录操作')
    TRANS_STATUS_ERROR  = ErrorEntry(1404, u'运单状态错误')
    DRIVER_QR_RELA_FAILED = ErrorEntry(1501, u'车牌已有司机绑定')
    DRIVER_QR_CODE_INVALID = ErrorEntry(1502, u'无效的司机二维码')
    DRIVER_QR_CODE_EXPIRED = ErrorEntry(1503, u'司机二维码已过期')
    NO_TRUCK            = ErrorEntry(1601, u'车辆不存在')
    NO_QR_RS            = ErrorEntry(1701, u'车辆未绑定司机')
    NO_LINE             = ErrorEntry(1702, u'线路不存在')
    DRIVER_HAS_BOUND_PLATE = ErrorEntry(1703, u'司机已绑定车牌')
    NO_CQ               = ErrorEntry(1704, u'未获取到车签号')
    CQ_IS_EXIST         = ErrorEntry(1801, u'车签已存在')
    PLATE_NO_SAME       = ErrorEntry(1802, u'建立关联关系的两个运单车牌不一致')
    TRANS_HAVE_LINKED   = ErrorEntry(1803, u'运单已经被关联')
    TIME_MATCH_ERROR    = ErrorEntry(1804, u'客户端时间与服务器时间不匹配')


class ErrorDefsDriver:
    __ver__ =u'1.0'
    __BASE__ = 20000

    OK                      = ErrorEntry( 1000 ,u'success成功')
    DB_ERROR                = ErrorEntry( 1001 ,u'服务器打了个盹')
    SERVER_ERR              = ErrorEntry( 1004 ,u'服务器开小差啦')
    REFRESH                 = ErrorEntry( 1005 ,u'刷新回调')
    NO_PERMIT               = ErrorEntry( 1008 ,u'未获取到运单信息')
    AUTH_FAIL               = ErrorEntry( 1100 ,u'密码输入错误，请重新输入')
    TOKEN_INVALID           = ErrorEntry( 1101 ,u'您的帐号登录已过期失效，请重新登录')
    NO_USER                 = TOKEN_INVALID
    NO_DRIVER               = TOKEN_INVALID
    NO_USER_EXIST           = ErrorEntry( 1102 ,u'该手机号未注册')
    NO_DRIVER_EXIST         = NO_USER_EXIST
    USER_OUT                = ErrorEntry( 1103 ,u'您的帐号已在其他手机登录')
    USER_EXIST              = ErrorEntry( 1104 ,u'该手机号已被注册')
    REGISTER_ERR            = ErrorEntry( 1105 ,u'网络连接失败，请检查网络')
    NOT_DRIVER              = ErrorEntry( 1106 ,u'请使用司机端APP注册')
    PASSWD_ERR              = ErrorEntry( 1107 ,u'原密码输入错误，请重新输入')
    USER_NOT_ACTIVE         = ErrorEntry( 1201 ,u'请修改初始密码')
    NO_TNUMBER              = ErrorEntry( 1302 ,u'运单不存在')

    SMS_EXPIRE              = ErrorEntry( 1303 ,u'验证码已过期, 请重新获取')
    PARAMS_ERROR            = ErrorEntry( 1304 ,u'参数类型错误')
    SMS_ERROR               = ErrorEntry( 1305 ,u'验证码错误,请重新输入')
    SMS_SENDED              = ErrorEntry( 1306 ,u'验证码已发送，请稍后再试')
    TRANS_FINISHED          = ErrorEntry( 1308 ,u'运单已完成，无法进行异常上报')
    NO_LOCATION             = ErrorEntry( 1401 ,u'没有此location编码')
    DRIVER_QR_RELA_FAILED   = ErrorEntry( 1501 ,u'绑定失败')
    NO_TRUCK                = ErrorEntry( 1601 ,u'未找到对应的车辆信息')
    NO_QR_RS                = ErrorEntry( 1701 ,u'未绑定车辆')

    EXCEPTION_EXIST = ErrorEntry(1805, u'重复上报异常')


class ErrorDefsCarrier:
    __ver__ =u'1.0'
    __BASE__ = 30000

    OK                  = ErrorEntry(1800,u'success')
    SERVER_ERR          = ErrorEntry(1801,u'server err!')
    LOGIN_FAIL          = ErrorEntry(1817,u'login fail!')
    NOT_ALLOW           = ErrorEntry(1803,u'not allow!')
    COMMITED            = ErrorEntry(1804,u'commited')
    REGISTERED          = ErrorEntry(1805,u'registered')
    NO_USER             = ErrorEntry(1806,u'no user')
    METHOD_ERR          = ErrorEntry(1807,u'method err!')
    NO_DATA             = ErrorEntry(1808,u'no data')
    TEMP_TOKEN          = ErrorEntry(1809,u'tmp token')
    PASSWD_EXPIRE       = ErrorEntry(1810,u'token expire')
    DB_ERROR            = ErrorEntry(1811,u'db err')
    CHECKED             = ErrorEntry(1812,u'已审核')
    ADMIN_USER          = ErrorEntry(1813,u'admin user')
    NO_TOKEN            = ErrorEntry(1814,u'NO TOKEN')
    PASSWD_ERR          = ErrorEntry(1816,u'passwd error!')
    TOKEN_EXPIRE        = ErrorEntry(1802,u'token expire!')
    PARAMS_ERR          = ErrorEntry(1818,u'params_err!')
    NO_SHIPPER          = ErrorEntry(1819,u'no shipper')
    NO_MATCH_DATA       = ErrorEntry(1820,u'no match data')
    SHIPPER_NO_COMMIT   = ErrorEntry(1821,u'shpper have no committed')
    TRUCK_EXISTS        = ErrorEntry(1822,u'truck exists')


errordefs = (ErrorDefsDispatcher,ErrorDefsCarrier,ErrorDefsDriver)

def reIndex():
    for defs in errordefs:
        kvs = hash_object( defs)
        for k,v in kvs.items():
            v.value+= defs.__BASE__
            print defs,':',k,'=',v.value,v.comment



