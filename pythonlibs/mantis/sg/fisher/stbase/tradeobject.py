#coding:utf-8

from base import *

class TradeObject(object):
    """交易标的物，可以是股票或合约"""
    def __init__(self,code,product):
        from position import Position

        self.code = code
        self.max_price = 0  # 当日最高限价
        self.min_price = 0  # 当日最低限价

        self.fee = 0        # 手续费
        self.price = Price()   # 最新价格
        self.product = product  # 产品：股票、期货
        # self.yd_close_ = 0   # 昨日收盤價
        self.inited = False
        self.pos = Position()

    def setPrice(self,price):
        self.price = price
        self.max_price = self.yd_close * 1.1
        self.min_price = self.yd_close * 0.9

    @property
    def limit_price(self):
        return self.max_price,self.min_price

    @property
    def last_price(self):
        """最新成交价格"""
        price = 0
        if self.price:
            price = self.price.last
        return price

    @property
    def yd_close(self):
        """昨日收盘价"""
        return self.price.yd_close

        # if not self.yd_close_:
        #     self.yd_close_ = self.product.market.getYdClosePrice(self.code)
        # return self.yd_close_

    def onTick(self,tick):
        pass

    def subTick(self):
        self.product.market.subTick(self.code,self.onTick)

    def dict(self):
        return dict(code=self.code)