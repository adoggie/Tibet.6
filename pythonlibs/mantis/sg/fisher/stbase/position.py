#coding:utf-8

from base import *

class Position(object):
    """持仓记录"""
    def __init__(self):
        from product import Product

        self.strategy_id = '' # 可以与具体的策略关联
        self.code = ''          # 股票代码
        self.product = Product.STOCKS   # 默认股票
        self.direction = Constants.Buy
        self.oc = Constants.Open        # 默认买开
        self.hedge = Constants.SPEC
        self.qty_current = 0    # 持仓余额(清算之后持仓) 包括可交易和冻结数量
        self.qty_pos = 0        # 实时持仓  同 qty_current
        self.qty_td = 0         # 今日持仓
        self.qty_yd = 0         # 昨仓 今日可用数量
        self.qty_yd_frozen = 0  # 昨冻结
        self.qty_td_frozen = 0  # 今冻结
        self.margin_amount = 0  # 保证金占用
        self.open_avg_price = 0 # 开仓均价
        self.cost_amount = 0    # 成本金额

    def dict(self):
        return hash_object(self)

    def json(self):
        return json.dumps(self.dict())