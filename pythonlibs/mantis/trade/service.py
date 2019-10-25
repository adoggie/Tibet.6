#coding:utf-8

import time
import os
import string
from threading import Thread,Timer
from mantis.fundamental.application.app import instance
from mantis.fundamental.service import ServiceBase
from mantis.fundamental.basetype import ValueEntry
from .types import ServiceType,TimeDuration
from .table import ServiceRuntimeTable
from mantis.trade.constants import *
from mantis.trade import command
from mantis.trade.message import *

class TimedTask(object):
    SECOND = 1
    MINUTE = SECOND * 60

    def __init__(self,action,user_data =None,timeout= SECOND):
        self.action = action
        self.timeout = timeout
        self.start_time = 0
        self.user = user_data
        self.times = 0

    def start(self):
        self.start_time = time.time()
        self.timer = Timer(self.timeout, self.action, (self,))
        self.timer.start()

    def stop(self):
        self.start_time = 0

    def execute(self):
        if self.start_time and self.start_time + self.timeout < time.time():
            self.start_time = time.time()
            if self.action:
                self.action(self)
                self.times+=1

class ServiceRunStatus(object):
    STOPPED = 'stopped'
    RUNNING = 'running'
    PAUSED  = 'paused'

class ServiceCommonProperty(object):
    ServiceId   = ValueEntry('service_id',u'系统编号')
    ServiceType = ValueEntry('service_type',u'服务类型')
    Host        = ValueEntry('host',u'主机地址')
    LiveTime    = ValueEntry('live_time',u'最近一次活跃时间 ')
    StartTime   = ValueEntry('start_time',u'运行开始时间')
    Status      = ValueEntry('status',u'运行状态 STOPPED/RUNNING/PAUSED')
    LauncherId  = ValueEntry('launcher_id',u'装载器编号')
    PID         = ValueEntry('pid',u'进程号')
    AccessUrl   = ValueEntry('access_url',u'管理接口')
    LogUrl      = ValueEntry('log_url',u'日志输出接口 ')

class ServicePropertyFrontLauncher(object):
    TradeAdapterIDs     = ValueEntry('trade_adapter_ids',u'资金交易适配程序编号')
    MarketAdapterIDs    = ValueEntry('market_adapter_ids',u'行情适配服务编号')

# class ProductClass(object):
#     Future = ValueEntry('future',u'期货')
#     Stock   = ValueEntry('stock',u'股票')

class ServicePropertyFrontService(object):
    """这里指 market , trade 前端接入服务"""
    ProductClass    = ValueEntry('product_class',u'产品类型')
    Exchange        = ValueEntry('exchange',u'交易市场')
    Gateway         = ValueEntry('gateway',u'')
    Broker          = ValueEntry('broker',u'期货公司')
    User            = ValueEntry('user',u'开户名称')
    Password        = ValueEntry('password',u'账户密码')
    MarketServerAddress    = ValueEntry('market_server_address',u'行情服务器')
    TradeServerAddress  = ValueEntry('trade_server_address',u'交易服务器')
    AuthCode = ValueEntry('auth_code',u'登陆用户认证码')
    UserProductInfo = ValueEntry('user_product_info',u'用户产品信息')

class ServicePropertyMarketAdapter(object):
    SubscribeContracts  = ValueEntry('subscribe_contracts',u'准备订阅的合约编号')

class TradeFrontServiceTraits():
    def __init__(self):
        # TradeAccountInfo.__init__(self)
        pass

    def syncDownServiceConfig(self):
        # self.product_class  = self.cfgs_remote.get(ServicePropertyFrontService.ProductClass.v)
        # self.gateway  = self.cfgs_remote.get(ServicePropertyFrontService.Gateway.v)
        # self.exchange        = self.cfgs_remote.get(ServicePropertyFrontService.Exchange.v)
        # self.broker         = self.cfgs_remote.get(ServicePropertyFrontService.Broker.v)
        # self.user           = self.cfgs_remote.get(ServicePropertyFrontService.User.v)
        # self.password       = self.cfgs_remote.get(ServicePropertyFrontService.Password.v)
        # self.market_server_addr = self.cfgs_remote.get(ServicePropertyFrontService.MarketServerAddress.v)
        # self.trade_server_addr  = self.cfgs_remote.get(ServicePropertyFrontService.TradeServerAddress.v)
        # self.auth_code  = self.cfgs_remote.get(ServicePropertyFrontService.AuthCode.v)
        # self.user_product_info  = self.cfgs_remote.get(ServicePropertyFrontService.UserProductInfo.v)
        pass

    # def convertToVnpyGatewayConfig(self):
    #     cfgs = dict( userID = self.user,
    #                  password = self.password,
    #                  brokerID = self.broker,
    #                  tdAddress = self.trade_server_addr,
    #                  mdAddress = self.market_server_addr
    #                  )
    #     if self.auth_code:
    #         cfgs['authCode'] = self.auth_code
    #
    #     if self.user_product_info:
    #         cfgs['userProductInfo'] = self.user_product_info
    #     return cfgs

class TradeService(ServiceBase):
    def __init__(self,name):
        super(TradeService,self).__init__(name)
        self._thread = None
        self.isclosed = False
        self.timed_taskes =set()
        self.service_id = None
        self.service_type = ServiceType.UnDefined
        self.table = None

        self.cfgs_remote = {}       # 存储在 redis 中的服务配置参数
        self.access_url = ''
        self.log_url = ''
        self.fanout_switchers ={}

        self.logger = None
        self.process_lock = None
        self.channels = {}
        # 服务本地数据通道 :  get,sub,pub
        # get - 消息接收通道，消息持久不会丢失
        # sub - 消息接收通道, 消息丢失,只接收最新消息
        # pub - 消息发布通道, 外部用户订阅接收最新消息
        # put - 消息发布通道， 外部用户一次接收消息不丢失


    def getServiceId(self):
        return self.service_id

    def getServiceType(self):
        return self.service_type.value

    def init(self,cfgs):
        self.cfgs = cfgs
        self.table = ServiceRuntimeTable() #.instance()
        conn = instance.datasourceManager.get('redis').conn
        self.table.setRedis(conn)

        if not self.runningAsUniqueProcess():
            return

        host = 'localhost'
        pid = os.getpid()

        dict_ = {
            str(ServiceCommonProperty.LiveTime): time.time(),
            str(ServiceCommonProperty.ServiceId): self.getServiceId(),
            str(ServiceCommonProperty.ServiceType): self.getServiceType(),
            str(ServiceCommonProperty.Host): host,
            str(ServiceCommonProperty.StartTime): time.time(),
            str(ServiceCommonProperty.Status): ServiceRunStatus.RUNNING,
            str(ServiceCommonProperty.PID): pid
        }

        self.table.updateServiceConfigValues(self.getServiceId(), self.getServiceType(),**dict_)
        self.syncDownServiceConfig()
        # self.initCommandChannels()


    def initCommandChannels(self):
        """初始化命令通道，用于本地服务接收和发送消息"""
        channels = map(string.strip,self.cfgs.get('init_channels','get,sub,pub,put').strip().split(','))

        if 'get' in channels:
            addr = ServiceCommandChannelAddressGet.format(service_type=self.service_type,service_id = self.service_id)
            chan = self.createServiceCommandChannel(addr,self.handle_channel_get,open=True)
            self.registerCommandChannel('get',chan)
        if 'sub' in channels:
            addr = ServiceCommandChannelAddressSub.format(service_type=self.service_type,service_id = self.service_id)
            chan = self.createServiceCommandChannel(addr,self.handle_channel_sub,open=True)
            self.registerCommandChannel('sub',chan)

        if 'pub' in channels:
            addr = ServiceCommandChannelAddressPub.format(service_type=self.service_type, service_id=self.service_id)
            chan = self.createServiceCommandChannel(addr, open=True)
            self.registerCommandChannel('pub', chan)

        if 'put' in channels:
            addr = ServiceCommandChannelAddressPut.format(service_type=self.service_type, service_id=self.service_id)
            chan = self.createServiceCommandChannel(addr, open=True)
            self.registerCommandChannel('put', chan)

    def registerCommandChannel(self,name,channel):
        self.channels[name] = channel

    def createServiceCommandChannel(self,name,handler=None,open=False):
        """
        创建远程服务的消息收发通道
        :param name:   ds/channel_name/pubsub or queue
        :param handler:
        :return:
        """
        brokername, address, type_ = name.split('/')
        broker = instance.messageBrokerManager.get(brokername)
        channel = broker.createChannel(address, handler=handler, type_=type_)
        if open:
            channel.open()
        return channel


    def handle_channel_get(self,data,ctx):
        """处理发送进入的请求 , 数据队列式，不丢失"""
        pass

    def handle_channel_sub(self, data, ctx):
        """处理发送进入的请求 , 数据订阅式，丢失"""
        pass

    def initFanoutSwitchers(self,cfgs):
        from .fanout import FanoutSwitcher
        for cf in cfgs:
            fs = FanoutSwitcher(self,cf)
            self.fanout_switchers[fs.name] = fs

    def dataFanout(self,switcher,data,**names):
        fs = self.fanout_switchers.get(switcher)
        if fs:
            fs.fanout(data,**names)

    def syncDownServiceConfig(self):
        """下载通用的配置信息"""
        cfgs =  self.table.getServiceConfigValues(self.getServiceId(),self.getServiceType())
        self.access_url = cfgs.get(ServiceCommonProperty.AccessUrl,'')
        self.log_url = cfgs.get(ServiceCommonProperty.LogUrl,'')
        self.cfgs_remote = cfgs

    def start(self,block=False):
        self.initCommandChannels()
        self.registerTimedTask(self.updateLiveStatus,self)
        # self._thread = Thread(target=self._run)
        # self._thread.start()

    def stop(self):
        self.isclosed = True
        if self.process_lock:
            self.process_lock.unlock()

    def join(self):
        if self._thread:
            self._thread.join()


    def registerTimedTask(self,action,user=None,timeout=TimedTask.SECOND):
        let = TimedTask(action,user,timeout)
        self.timed_taskes.add(let)
        let.start()
        return let

    def unregisterTimedTask(self,let):
        let.stop()
        self.timed_taskes.remove(let) # don't worry about the lock protection

    def _run(self):
        self.isclosed = False

        while not self.isclosed:
            for task in self.timed_taskes:
                task.execute()
            time.sleep(0.1)

    def updateLiveStatus(self,task):
        """
        注册服务运行状态
        :return:
        """
        # print 'times:',task.times,'user:',task.user
        dict_=  {
            ServiceCommonProperty.LiveTime.v: time.time(),
        }
        self.table.updateServiceConfigValues(self.getServiceId(),self.getServiceType(),
                                             **dict_
                                             )
        self.broadcastServiceStatus()

        task.start()

    def runningAsUniqueProcess(self):
        """保持运行唯一进程"""
        if not self.cfgs.get('running_unique',False):
            return
        result = self.tryAcquireProccessLock()
        if not result:
            self.logger.error('Another Process Instance Is Runing , Please Kill it ,Then Restart Me.')
            instance.abort()
            return False
        self.registerTimedTask(self.keepUniqueProcessLock,timeout=TimeDuration.SECOND*1)
        return True

    def keepUniqueProcessLock(self,task):
        """保持进程锁"""
        result= self.process_lock.lock()
        # print 'Process Unique Lock:',result
        task.start()


    def tryAcquireProccessLock(self):
        from mantis.fundamental.redis.lock import Locker
        from mantis.fundamental.utils.useful import list_item_match
        if not self.process_lock:
            cfgs = list_item_match(instance.getConfig().get('datasources',[]),'name','redis')

            resid = TradeAvailableServiceLockFormat.format(str(self.service_type), self.service_id)
            servers = [dict(host=cfgs.get('host'), port=cfgs.get('port'), db=cfgs.get('db', 0))
                       ]
            self.process_lock = Locker(resid, ttl=TimeDuration.SECOND*5*1000,servers=servers)
        result = self.process_lock.lock()
        return result

    def broadcastServiceStatus(self):
        """在pub通道上广播自身服务的状态配置信息"""
        data = self.serviceStatusAndConfigs()
        message = Message(command.ServiceStatusBroadcast.NAME,data = data.__dict__)
        self.publishMessage(message)

    def serviceStatusAndConfigs(self):
        msg = command.ServiceStatusBroadcast()
        msg.service_id = self.service_id
        msg.service_type = str(self.service_type)
        service = instance.serviceManager.get('http')
        if service:
            http = service.cfgs.get('http',{})
            url = 'http://{host}:{port}'.format(host=http.get('host'),port=http.get('port'))
            msg.http = url
        return msg

    def publishMessage(self,message):
        """
        通过pub通道将消息发布给策略runner
        :param data:
        :return:
        """

        channel = self.channels.get('pub') #
        if not channel:
            return
        Request(channel).send(message)
