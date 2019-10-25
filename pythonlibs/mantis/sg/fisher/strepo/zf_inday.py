#coding:utf-8

"""
zf_inday.py

日内涨跌幅度
"""

import numpy as np
import talib as ta
from mantis.sg.fisher import stbase
from base import StrategyEntity,RegisteredStrategyEntities


class ZFInDay(StrategyEntity):
    def __init__(self,strategy = stbase.Strategy(None, None)):
        StrategyEntity.__init__(self, strategy)


    def init_default_params(self):
        """初始化缺省参数"""

        vals = dict( limit = .1 , num = 100 )
        return vals


    def onTick(self, tick):
        """日内涨跌幅策略
        @:param code: 股票代码
        @:param num ：买卖数量
        @:param limit: 价格浮动限

        当日仅仅允许买卖各触发一次

        """
        StrategyEntity.onTick(self,tick)

        status = self.current_status(tick.code)
        limit = status.limit
        num = status.num

        status.save()

        code = tick.code
        stock = stbase.stocks.getTradeObject(code)

        # zf = stock.last_price / stock.yd_close - 1
        zf = stock.price.diff_rate

        # strategy_name = 'strategy_inday'
        # st_price = stock.yd_close * (1 + limit)
        # st_price = round(st_price, 2)

        if zf <= -limit:
            st_price = stock.price.sell_1
            self.logger.takeSignal(stbase.StrategySignal(code, text='strategy_zf_inday, (zf <= -limit), '
                                                                    'zf:%s last_price:%s  yd_close_price:%s' %
                                                                    (zf, stock.last_price, stock.yd_close)
                                                         )
                                   )
            # 跌幅过限
            amount = self.st.product.getAmountUsable()
            # pos_sum = stock.pos.net_total
            pos = self.st.product.getPosition(code)
            if not pos:
                self.logger.debug('yd pos is 0. Exit..')
                stbase.controller.stop()
                return
            #
            if pos.cost_amount <= amount * 0.1 and not self.st.any.get('buy_order_req'):
                """持仓资金占总资金 <= 10% """
                self.logger.debug('do buy: {} ,{}, {}'.format(code, st_price, num))
                order_req = self.st.buy(code, st_price, num)
                self.st.any['buy_order_req'] = order_req
                self.st.any['current_order_req'] = order_req

        elif zf >= limit:
            """ """
            st_price = stock.price.buy_1
            self.logger.takeSignal(stbase.StrategySignal(code,
                                                         text='strategy_inday, (zf >= -limit), zf:%s last_price:%s  yd_close_price:%s' %
                                                              (zf, stock.last_price, stock.yd_close)
                                                         )
                                   )


            pos = self.st.product.getPosition(code)
            if not pos:
                self.logger.debug('yd pos is 0. Exit..')
                stbase.controller.stop()
                return
            
            if pos.qty_yd >= num and not self.st.any.get('sell_order_req'):
                self.logger.debug('do sell: {} ,{}, {}'.format(code, st_price, num))
                order_req = self.st.sell(code, st_price, num)
                self.st.any['sell_order_req'] = order_req
                self.st.any['current_order_req'] = order_req

        if self.st.any.get('current_order_req'):
            order = None
            order_req = self.st.any.get('current_order_req')
            self.logger.debug('query order:',order_req.order_id)
            # orders = Strategy.GetOrdersByOrigSerialNo(current_order_req.order_id)
            orders = self.st.getOrders(order_id= order_req.order_id )
            self.logger.debug('orders size:', len(orders))

            if orders:
                order = orders[0]
            if order:
                self.logger.debug('knockqty:', order.qty_filled)
                if order.qty_filled >= order_req.min_knock_num_rate * order_req.num:
                    if order_req.direction == stbase.Constants.Buy:
                        self.st.any['sell_order_req']  = None  # 允许开卖
                    if order_req.direction == stbase.Constants.Sell:
                        self.st.any['buy_order_req'] = None

                    self.st.any['current_order_req'] = None
                    # count += 1



# 策略到全局对象表
RegisteredStrategyEntities['ZFInDay'] = ZFInDay