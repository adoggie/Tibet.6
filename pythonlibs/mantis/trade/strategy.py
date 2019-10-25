#coding:utf-8

import json
from collections import OrderedDict
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.trade.types  import TradeAccountQuota
from mantis.trade.constants import  *



class StrategyTask(object):
    NAME = 'strategy_task'
    def __init__(self):
        self.name       = ''
        self.user       = ''  # 交易用户名称
        self.quotas     = TradeAccountQuota.EMPTY_LIST    #
        self.strategy   = StrategyInfo()
        self.start_time = 0

    def loads(self,cfgs):
        self.name = cfgs.get('name','')
        self.user = cfgs.get('user','')
        for q in cfgs.get('quotas',[]):
            quota = TradeAccountQuota()
            quota.name = q.get('name')
            quota.limit = q.get('limit')
            quota.account = q.get('account')
            quota.product = q.get('product')
            self.quotas[quota.account] = quota  # 账户名称作为key

        self.strategy.loads(cfgs.get('strategy',{}))

    def dumps(self):
        quotas = []
        for q in self.quotas.values():
            quotas.append(q)
        result=dict( name =self.name , user = self.user ,
                     quotas = quotas,
                     strategy=self.strategy.dumps()
                    )
        return result

class StrategyInfo(object):
    NAME = 'strategy'
    def __init__(self):
        self.id = ''        # base64( md5( 策略名称 +策略代码) )
        self.codes = {}      # 策略代码 , { name:content } ,例如: 'geniusbarmaker.py':'xxxxx'
        self.sum = ''       # 代码checksum
        self.configs ={}

    def loads(self, cfgs):
        object_assign(self,cfgs)

    def dumps(self):
        result = hash_object(self)
        return result


if __name__ == '__main__':
    st = StrategyTask()
