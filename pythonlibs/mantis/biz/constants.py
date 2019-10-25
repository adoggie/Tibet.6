#coding:utf-8

from camel.fundamental.basetype  import ValueEntry

class UserType:
    """
        Camel数据库
        1.用户表（User）
        1.1用户类型
        role_type
    """
    Driver              = ValueEntry(0, u'司机')
    Tuned               = ValueEntry(2, u'总调')
    Operations          = ValueEntry(3, u'运维')
    Abolisher           = ValueEntry(4, u'运单异常完成与废止专员')
    NewDriver           = ValueEntry(7, u'新增司机专员')
    CenterScheduling    = ValueEntry(1, u'中心调度')
    SchedulingPrimaryUsers          = ValueEntry(5, u'调度端初级用户')
    SchedulingAuditsCommissioner    = ValueEntry(6, u'调度端审核专员')

class UserSource:
    """
        1.2 用户注册来源
        source
    """
    BackgroundRegistration  = ValueEntry(0, u'后台注册')
    DriverSide              = ValueEntry(1, u'司机端')

class UserActive:
    """
        1.3 用户激活状态
        active
    """
    Inactive            = ValueEntry(0, u'未激活')
    Activated           = ValueEntry(1, u'已激活')

class TruckTempState:
    """
        2.车辆表（Truck）
        2.1车辆是否为临时车
        is_temp_truck
        关联：运单表（Transport_protocol）是否临时车is_temp_truck
    """
    NormalCar           = ValueEntry(0, u'正班车')
    TemporaryCar        = ValueEntry(1, u'临时车')

class TruckRunType:
    """
        2.2车辆运行方式
        run_mode
        关联：运单表（Transport_protocol）车辆运行方式run_mode
        关联：路线表（Line）车辆运行方式run_mode
    """
    OneWay              = ValueEntry(0, u'单边车')
    BothWay             = ValueEntry(1, u'双边车')

class TruckSettleType:
    """
        2.3车辆表的是否为可结算车型
        is_forbidden
    """
    DoNotSettle         = ValueEntry(0, u'不可结算')
    CanBeSettled        = ValueEntry(1, u'可结算')

class TruckDisableType:
    """
        2.4车辆表的车辆是否禁用
        if_valid
    """
    Disabled            = ValueEntry(0, u'不可用')
    Available           = ValueEntry(1, u'可用')

class TruckRunState:
    """
        2.5车辆表的车辆是否在途
        is_onway
        关联：运单表（Transport_protocol）运单最终状态is_onway
    """
    Transit             = ValueEntry(1,u'在途')
    Arrive              = ValueEntry(2, u'到达')

class TruckTrailerType:
    """
        2.6车辆表的车辆是否为挂车
        trailers
    """
    Nottrailer          = ValueEntry(0, u'非挂车')
    Trailer             = ValueEntry(1, u'挂车')

class TriggerType:
    """
        3.1触发记录表的触发类型
        trigger_type
    """
    Enter               = ValueEntry(1, u'进')
    Come                = ValueEntry(2, u'出')

class SubmitType:
    """
        3.2触发记录表的提交围栏类型
        comt_type
    """
    CloudFence          = ValueEntry(0, u'云围栏')
    OfflineFence        = ValueEntry(1, u'离线围栏')
    DropDown            = ValueEntry(2, u'下拉获取云围栏触发记录上报')
    Carsign             = ValueEntry(3, u'车签')

class LocationCodeType:
    """
        4.运单经过点记录表（Transport_protocol_relay）
        4.1运单经过点记录表的经过点编码类型
        location_code_type
    """
    StartCoding         = ValueEntry(1, u'起点编码')
    StoppingCoding      = ValueEntry(2, u'经停点编码')
    FinishCoding        = ValueEntry(3, u'终点编码')

class TransNumberStatus :
    """
            5.运单流状态表（Transport_protocol_flow）
            5.1运单中途状态
            Status
            关联：运单表（Transport_protocol）运单最终状态status
    """
    ToSignIn            = ValueEntry(201, u'待签到')
    ForLoading          = ValueEntry(300, u'待装车')
    Intransit           = ValueEntry(500, u'运输中')
    Completed           = ValueEntry(501, u'已完成')
    Abolished           = ValueEntry(301, u'已废止')
    Abnormal            = ValueEntry(503, u'异常待确认')
    ArtificialComplete  = ValueEntry(502, u'人工完成')
    InvalidWaybill      = ValueEntry(302, u'无效运单')

class TransNumberRelayStatus:
    """
        6.运单表（Transport_protocol）
        6.1运单中转状态
        relay_status
        中转状态，个位1：到达 2：出发；十位：经停顺序，index=1
        关联：司机到发车记录表（Transport_departure_arrival_record）到发车类型type
    """
    Arrival             = ValueEntry(1, u'到达')
    Depart              = ValueEntry(2, u'出发')

class TruckFrequencyType:
    """
        6.2是否加班车
        is_overtime
    """
    NormalFrequency     = ValueEntry(0, u'正班频次')
    AbnormalFrequency   = ValueEntry(1, u'加班频次或者临时线路')

class TransNumberReturnType:
    """
        6.3是否一车往返
        is_link
    """
    Notreturn           = ValueEntry(0, u'不往返')
    Return              = ValueEntry(1, u'往返')

class TransportRecordType:
    """
        7.司机到发车记录表（Transport_departure_arrival_record）
        7.1记录类型
        source_type
    """
    #Cloud_Fence_Or_Scheduling_ Operation = ValueEntry(null, '云围栏or调度端到发操作')
    CloudFence          = ValueEntry(0, u'云围栏')
    OfflineFence        = ValueEntry(1, u'离线围栏')
    ServiceFence        = ValueEntry(2, u'服务端围栏检测数据')
    CarSign             = ValueEntry(3, u'车签到发数据')
    SchedulingOperation = ValueEntry(4, u'调度端到发操作')
    CollectionOperation = ValueEntry(5, u'补录专员操作')

class DriverBindingType:
    """
        8.司机绑定解绑表（Qr_record）
        8.1绑定解绑类型
        operator_type
    """
    Binding             = ValueEntry(1, u'司机绑定')
    Unbundling          = ValueEntry(2, u'司机解绑')
    Kicked              = ValueEntry(3, u'司机被踢')

class DeviceType:
    """
        9.登录记录表（Login）
        9.1设备类型
        device_type
    """
    Pc                  = ValueEntry(0, u'pc')
    Ios                 = ValueEntry(1, u'ios')
    Android             = ValueEntry(2, u'android')

class LoginType:
    """
        9.2登录类型
        login_type
    """
    Login               = ValueEntry(0, u'登进')
    Exit                = ValueEntry(1, u'登出')

class LineUseType:
    """
        10.路线表（Line）
        10.1线路使用状态
        status
    """
    Unused              = ValueEntry(0, u'未使用')
    Used                = ValueEntry(1, u'已使用')

class LineType:
    """
        10.2线路类型
        line_status
    """
    Normal              = ValueEntry(2, u'正式')
    Temporary           = ValueEntry(4, u'临时')

class LineFrequencyType:
    """
        10.3频次类型
        fre_status
    """
    Valid               = ValueEntry(u'vaid', u'有效')
    Invalid             = ValueEntry(u'invalid', u'无效')

class FenceTriggerType:
    """
        11.围栏记录表（Fence_record）
        11.1触发方式
        trigger_type
    """
    CloudFence          = ValueEntry(0, u'云围栏')
    OfflineFence        = ValueEntry(1, u'离线围栏')
    ManuallRefresh      = ValueEntry(2, u'手动刷新')

class FenceStatus:
    """
        12.围栏表（Fence）
        12.1围栏状态
        status
    """
    Create              = ValueEntry(1, u'创建')
    Trigger             = ValueEntry(2, u'触发')

class AbnormalType:
    """
        13.异常上报记录表（Driver_live_reporting）
        13.1异常类型
        report_type
    """
    TrafficJam          = ValueEntry(2000, u'堵车')
    AbnormalWeather     = ValueEntry(2100, u'异常天气')
    VehicleFailure      = ValueEntry(2500, u'车辆故障')
    GoSlow              = ValueEntry(2800, u'缓行')
    Detour              = ValueEntry(2900, u'绕行')

class AbnormalUploadType:
    """
        13.2上传类型
        flag
        0;10分号前表示开,分号后表示关
    """
    Upload              = ValueEntry(u'(第一位)0', u'直接上传')
    OfflineUpload       = ValueEntry(u'(第一位)1', u'离线上传')
    Manual              = ValueEntry(u'(第二位)0', u'手动')
    Automatic           = ValueEntry(u'(第二位)1', u'自动')

class ScanType:
    """
        14.调度扫描记录表（Dispatcher_scan_record）
        14.1到发车扫描
        scan_type
    """
    EndScanning         = ValueEntry(1, u'到车扫描')
    StartScanning       = ValueEntry(2, u'发车扫描')

#--------------------------Carrier数据库--------------------------
class CarrierUserType:
    """
        Carrier数据库
        1.用户表（Users）
        1.1用户类型
        com_type
    """
    Company             = ValueEntry(0, u'公司')
    Personal            = ValueEntry(1, u'个人')

class CarrierUserRole:
    """
        1.2用户来源
        role
    """
    OrdinaryUser        = ValueEntry(0, u'普通用户')
    InternalUser        = ValueEntry(1, u'圆通内部用户')

class ShippersStatus:
    """
        2.承运商表（Shippers）
        2.1车辆状态
        status
        关联：项目车辆表（Project_truck_type）车辆状态status
    """
    Empty               = ValueEntry(0, u'空')
    TemporaryStorage    = ValueEntry(1, u'临时保存')
    Submitted           = ValueEntry(1, u'已提交')

class TruckLengthType:
    """
        3.车辆类型表（Truck_type）
        3.1车长类型
        Length
    """
    L0                  = ValueEntry(0, u'0')
    L960                = ValueEntry(960, u'960')
    L1470               = ValueEntry(1470, u'1470')
    L1750               = ValueEntry(1750, u'1750')

class CommitsStatus:
    """
        4.审核表（Commits）
        4.1审核状态
        status
    """
    NotAudit            = ValueEntry(0, u'未审核')
    Approved            = ValueEntry(1, u'审核通过')
    Unapprove           = ValueEntry(2, u'审核不合适')
    InformationPerfect  = ValueEntry(3, u'资料待完善')

class CommitsCollectType:
    """
        4.2是否收藏
        star
    """
    Uncollected         = ValueEntry(0, u'未收藏')
    Collected           = ValueEntry(1, u'已收藏')

class CarriageType:
    """
        5.车辆表（Camel_truck）
        5.1车厢类型
        carriage_type
        关联：车辆表（Trucks）车辆状态carriage_type
    """
    Van                 = ValueEntry(1, u'厢式')
    Gaolan              = ValueEntry(2, u'高栏')

class TruckType:
    """
        5.2车辆类别
        truck_type
        关联：车辆表（Trucks）车辆状态truck_type
    """
    GeneralFreight      = ValueEntry(1, u'一般货车')
    Hangcar             = ValueEntry(2, u'挂车头')
    HangCompartments    = ValueEntry(2, u'挂厢')

class TruckStatus:
    """
        5.3车辆状态
        truck_status
    """
    Normal              = ValueEntry(1, u'正常')
    Cancellation        = ValueEntry(2, u'注销')

class BidStatus:
    """
        6.竞标结果表（Bid_result）
        6.1状态
        status
    """
    Candidate           = ValueEntry(0, u'候选')
    NotBargaining       = ValueEntry(1, u'待议价')
    Winning             = ValueEntry(2, u'中标')
    NotWinning          = ValueEntry(3, u'未中标')

class RunMode:
    """
        7.项目表（Project）
        7.1行驶方式
        run_mode
    """
    Vehicle             = ValueEntry(1, u'整车')
    LCL                 = ValueEntry(2, u'零担')
    VehicleWithLCL      = ValueEntry(3, u'整车加零担')

class MajorTruckType:
    """
        7.2主力车型
        major_truck
    """
    T1                  = ValueEntry(1, u'0')
    T2                  = ValueEntry(2, u'9.6')
    T3                  = ValueEntry(3, u'14.7')
    T4                  = ValueEntry(3, u'17.5')

class ProjectStatus:
    """
        7.3项目状态
        status
    """
    NotRelease          = ValueEntry(1, u'未发布')
    Release             = ValueEntry(2, u'发布')
    Bidding             = ValueEntry(3, u'招标中')
    EndBiding           = ValueEntry(3, u'报价结束')

class BidOrderTimes:
    """
        8.竞标路线价格表（Bid_line_price）
        8.1第几轮报价最低价
        order_times
    """
    InitialOffer        = ValueEntry(0, u'初始报价')
    FirstRound          = ValueEntry(1, u'第一轮')
    SecondRound         = ValueEntry(2, u'第二轮')
    ThirdRound          = ValueEntry(3, u'第三轮')

class TruckAuditType:
    """
        9.车辆表（Trucks）
        9.1车辆审核通过值
        commit_status
    """
    NotThrough          = ValueEntry(0, u'未通过')
    Through             = ValueEntry(1, u'通过')


