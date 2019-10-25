#coding:utf-8

from vnpy.trader.vtObject import VtContractData,VtContractCommissionRateData,VtDepthMarketData


class TradeContractData(VtContractData,VtDepthMarketData,VtContractCommissionRateData):
    def __init__(self):
        VtContractData.__init__(self)
        VtContractCommissionRateData.__init__(self)
        VtDepthMarketData.__init__(self)

    def dict(self):
        return dict(symbol = self.symbol,
                    exchange = self.exchange,
                    size = self.size ,
                    priceTick = self.priceTick,
                    max_market_order_volume = self.MaxMarketOrderVolume,
                    min_market_order_volume = self.MinMarketOrderVolume,
                    max_limit_order_volume = self.MaxLimitOrderVolume,
                    min_limit_order_volume = self.MinLimitOrderVolume,
                    long_margin_ratio = self.LongMarginRatio,
                    short_margin_ratio = self.ShortMarginRatio,
                    upper_limit_price = self.UpperLimitPrice,
                    lower_limit_price = self.LowerLimitPrice,
                    open_ratio_by_money = self.OpenRatioByMoney,
                    open_ratio_by_volume = self.OpenRatioByVolume,
                    close_ratio_by_money = self.CloseRatioByMoney,
                    close_ratio_by_volume = self.CloseRatioByVolume,
                    close_today_ratio_by_money = self.CloseTodayRatioByMoney,
                    close_today_ratio_by_volume = self.CloseTodayRatioByVolume

                    )