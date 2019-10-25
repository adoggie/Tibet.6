#coding:utf-8

"""
simple ma

简单均线买卖
"""

import numpy as np
import talib as ta
from mantis.sg.fisher import stbase
from base import StrategyEntity,RegisteredStrategyEntities


class SimpleMA(StrategyEntity):
    def __init__(self,strategy = stbase.Strategy(None, None)):
        StrategyEntity.__init__(self, strategy)

    def execute(self,code, cycle):
        """计算均线策略
            MA - 简单算术均线 talib.SMA
            EMA － 滑动 指数移动均线

        """
        # close = get_bars(code, interval)
        stock = stbase.stocks.getTradeObject(code)
        # bars : stbase.BarData()
        bars = stock.market.getHistoryBars(cycle, limit=30)
        close = map(lambda _: _.close, bars)  # 收盘价格列表

        close = np.array(close)
        self.logger.debug('size:%s' % len(close))

        print close.tolist()

        # stbase.print_line(close.tolist())
        print 'to ma calculating...'
        ma5 = ta.MA(close, 5)

        ma10 = ta.MA(close, 10)

        a, b = ma5[-2:]
        c, d = ma10[-2:]

        # strategy_name = 'strategy_ma'
        print 'ma5:', ma5
        print 'ma10:', ma10
        # self.logger.debug('=={}=={}=='.format(code, interval))
        self.logger.debug('(strategy_ma) ma5:{}'.format(ma5.tolist()))
        self.logger.debug('(strategy_ma) ma10:{}'.format(ma10.tolist()))

        self.logger.debug('(strategy_ma）a:{} b:{} c:{} d:{}'.format(a, b, c, d))

        last_price = stbase.stocks.getTradeObject(code).last_price # 最近价格

        if b >= d and a < c and self.st.any.get('ma_buy_count').get(code, 0):
            num = 100
            self.logger.takeSignal(stbase.StrategySignal(code,text='strategy_ma, (b >= d and a< c), a:{} b:{} c:{} d:{}'.format(a, b, c, d)))
            amount = self.strategy.product.getAmountUsable() # 获取可用资金数

            cost = last_price * num
            if cost <= amount * 0.1:
                self.logger.debug('do buy: {} , {} , {}'.format(code, last_price, num))
                self.st.buy(code,last_price,num,msg='strategy_ma , (b >= d and a< c) ,a:{} b:{} c:{} d:{}'.format(a, b, c, d))
                self.st.any.get('ma_buy_count')[code] = 1

        if b <= d and a > c and self.st.any.get('ma_sell_count').get(code, 0):
            num = 100
            self.logger.takeSignal(stbase.StrategySignal(code,
                                                         text='strategy_ma, (b <=d and a > c), a:{} b:{} c:{} d:{}'.format(
                                                             a, b, c, d)))
            pos = self.st.product.getPosition(code)
            if num <= pos.qty_td:
                self.logger.debug('do sell: {} ,{}, {}'.format(code, last_price, num))
                self.st.sell(code,last_price,num,msg='strategy_ma signal occur.  (b <=d and a > c),a:{} b:{} c:{} d:{}'.format(a, b, c, d))
                self.st.any.get('ma_sell_count')[code] = 1


# ---------------------------------------------------
# 策略到全局对象表
RegisteredStrategyEntities['SimpleMA'] = SimpleMA