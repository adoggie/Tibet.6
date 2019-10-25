#coding:utf-8


import time,datetime
from collections import OrderedDict
from functools import partial
from utils.importutils import import_module
from utils.useful import singleton
import stbase
import ams

class ASM_Strategy(stbase.Strategy):
    def __init__(self,name,product):
        stbase.Strategy.__init__(self,name,product)

    def init(self,*args,**kwargs):
        stbase.Strategy.init(self,*args,**kwargs)
        return self

    def onTick(self,tick):
        """
        :param tick:  stbase.TickData
        :return:
        """
        print tick

    def onBar(self,bar):
        """

        :param bar: stbase.BarData
        :return:
        """
        print bar

def init(context):
    stbase.controller.init('z:/ams/fisher')
    stbase.stocks.setup(ams.ASM_StockMarket().init(context), ams.ASM_StockTrader().init(context))
    stbase.stocks.market.setupRecorder(stbase.MarketFileRecorder(stbase.controller.data_path)) # 安裝行情記錄器
    stbase.controller.addStrategy(ASM_Strategy('ASM_Strategy',stbase.stocks).init())
    stbase.controller.run()
    stbase.println("Strategy : Sample Started..")

"""

import sys
import os 
import time
import threading
import ctypes

# 添加py運行路徑的方式在 ams的策略列表啟動會報錯， 而直接從菜單創建并運行則okay
# 重啟了ams之後策略列表運行報錯

sys.path.append('F:/Projects/Branches')
from mantis.sg.fisher.ams import Context
Context().init(Market,Strategy)
Context().ResTable.OrderItem = OrderItem
Context().launch('mantis.sg.fisher.strategy_ams_sample')

（1）交易端首页登录账号/密码：zssp000/xyzq601377；
其现货资金账号/密码：30073627/112233

兴业-云服务器账号
================
账号：XYXY001
密码：XYXY0000

"""
