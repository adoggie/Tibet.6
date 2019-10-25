#coding:utf-8

from collections import OrderedDict
from mantis.sg.fisher import stbase


class StrategyEntity(object):
    """策略算法执行实体基类"""
    def __init__(self,strategy = stbase.Strategy(None,None) ):
        self.entity_id = ''
        self.strategy = strategy
        self.st = strategy
        self.logger = self.strategy.getLogger()
        # self.params = None  # ORM : model.CodeSettings

    # def set_params(self,**kwargs):

    def init_default_params(self):
        """初始化缺省参数"""
        return dict()

    # @property
    # def id(self):
    #     if not self.entity_id:
    #         return self.__class__.__name__
    #     return self.entity_id

    def onExec(self, code, **kwargs):
        # self.params = self.strategy.get_code_params(code)
        # vals = self.init_default_params()
        # for k,v in vals.items():
        #     if not hasattr(self.params,k):
        #         setattr(self.params,k,v)
        pass

    def current_status(self,code):
        params = self.strategy.get_code_params(code)
        vals = self.init_default_params()
        for k, v in vals.items():
            if not hasattr(params, k):
                setattr(params, k, v)
        return params

    # 三种触发行为
    def onTick(self,tick):
        self.onExec(tick.code)

    def onBar(self,bar):
        self.onExec(bar.code)

    def onTimer(self, timer):
        code = timer.user
        timeout = timer.timeout
        self.onExec(code)


# 全局的交易策略对象注册表
RegisteredStrategyEntities = OrderedDict() # {id:entity}

def initialEntity(name,strategy):
    CLS = RegisteredStrategyEntities.get(name)
    if not CLS:
        return None
    entity = CLS(strategy)
    return entity
