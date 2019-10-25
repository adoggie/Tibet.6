#coding:utf-8

"""交易状态机"""

class State(object):
    def __init__(self):
        self.predicate = None #
        self.data = OrderedDict()

    def chained(self,behavior,state):
        """连接下一个状态， 通过行为事件来触发状态迁移"""
        pass

    def enter(self,prev = None):
        """由前一个状态切换到此"""
        pass

    def leave(self):
        """切换到下一个状态"""
        pass

class Behavior(object):
    def __init__(self):
        pass

    def state(self):
        """行为导致状态改变"""
        pass

    def run(self):
        pass


class BehaviorBuy(Behavior):
    """买入"""
    def __init__(self):
        Behavior.__init__(self)

class BehaviorCancelOrder(Behavior):
    """撤单"""
    def __init__(self):
        Behavior.__init__(self)

class StateStart(State):
    def __init__(self): State.__init__(self)

class StateEnd(State):
    def __init__(self): State.__init__(self)

class StateBuy(State):
    def __init__(self,expire = 10):
        State.__init__(self)

    def onFull(self):
        """全成"""
        pass

    def onPartial(self,partial,all):
        """部成"""
        pass

    def onTimeout(self, num):
        """超时 , num: 已成"""

class StateCancelOrder(State):
    def __init__(self,expire = 10):
        State.__init__(self)

class BehaviorEval(State):
    """"""
    def __init__(self,times):
        State.__init__(self)

class BehaviorSet(object):
    def __init__(self):
        pass

    def run(self):
        pass

class StateWait(State):
    """等待"""
    def __init__(self,times):
        State.__init__(self)

class StateMachine(object):
    """交易运行状态机"""
    def __init__(self,code):
        self.states = [ ] # 状态集合
        pass

    def run(self):
        pass

    def stop(self):
        pass

