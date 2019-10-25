#coding:utf-8

# stalgorithm.py

# 策略算法集合

# #计算MACD线
import pandas as pd
import numpy as np
from datetime import datetime as Datetime,time as Time
from dateutil.parser import parse
from dateutil.rrule import *


import talib as ta

'''
# pandas 0.22 包含
'''
def MACD(price, fastperiod=12, slowperiod=26, signalperiod=9):
    ewma12 = pd.ewma(price,span=fastperiod)
    ewma60 = pd.ewma(price,span=slowperiod)
    dif = ewma12-ewma60
    dea = pd.ewma(dif,span=signalperiod)
    bar = (dif-dea)     #有些地方的bar = (dif-dea)*2，但是talib中MACD的计算是bar = (dif-dea)*1
    return dif,dea,bar*2 # 国内交易软件 * 2

"""

df = ts.get_hist_data('600000', start='2018-06-01')
df = df.sort_index()
close = df['close'].values

vs = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

#talib的 macd 返回 vs（对应diff），macdsignal（对应dea），macdhist（对应macd）。

# print df.shape[0] # 记录集行数 or len(df)

dif,dea,bar = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
vs = dif,dea,bar
df['diff']  = vs[0]
df['dea']  = vs[1]
df['macd']  = vs[2] * 2

#导出
xdf = df[['close','diff','dea','macd']]
xdf.to_csv("macd.csv")
#绘图
xdf = df[['diff','dea','macd']]
xdf.plot()
"""


# Talib 常用代码
# http://30daydo.com/article/196
