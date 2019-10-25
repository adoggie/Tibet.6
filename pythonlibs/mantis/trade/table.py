# coding:utf-8

from .types import ServiceType
from constants import *

# ConfigNames={
#     ServiceType.DataPAServer.v:       'trade.available.data_pa_server',
#     ServiceType.DataResourceServer.v: 'trade.available.data_res_server',
#     ServiceType.FrontLauncher.v:      'trade.available.front_launcher',
#     ServiceType.StrategyLauncher.v:   'trade.available.strategy_launcher',
#     ServiceType.GlobalDispatcher.v:   'trade.available.dispatcher',
#     ServiceType.MarketAdapter.v:      'trade.available.market_adapter',
#     ServiceType.TradeAdapter.v:       'trade.available.trade_adapter',
#     ServiceType.TradeServer.v:        'trade.available.trade_server',
#     ServiceType.StrategyRunner.v:     'trade.available.strategy_runner',
#     ServiceType.StrategyDevRunner.v:  'trade.available.strategy_dev_runner'
# }

# @singleton
class ServiceRuntimeTable(object):
    def __init__(self,redis_ = None):
        self.redis = redis_

    def setRedis(self,redis_):
        self.redis = redis_
        return self

    def configPrefixByServiceType(self,type_):
        """根据服务类型返回 key 定义前缀"""
        return TradeAvailableServiceTypeFormat.format(str(type_))
        # return ConfigNames.get(str(type_),'')

    def getServiceIdsByType(self,type_):
        """查询指定服务类型的服务进程编号"""
        key = self.configPrefixByServiceType(type_) + '.*'
        return  self.redis.keys(key)

    def getServiceConfigValues(self,service_id,type_):
        # key = self.configPrefixByServiceType(type_)+'.'+service_id
        key = self.getServiceUniqueName(type_,service_id)
        values = self.redis.hgetall(key)
        return values

    def getServiceUniqueName(self,type_,service_id):
        return TradeAvailableServiceFullNameFormat.format(str(type_),service_id)

    def updateServiceConfigValues(self,svc_id,type_,**value):
        key = self.getServiceUniqueName(type_, svc_id)
        dict_ = {}
        for k,v in value.items():
            dict_[str(k)] = v
        self.redis.hmset(key,dict_)

    def removeServiceConfig(self,service_id,type_):
        key = self.getServiceUniqueName(type_, service_id)
        self.redis.delete(key)
