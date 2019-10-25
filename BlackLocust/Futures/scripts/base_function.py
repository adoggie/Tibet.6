# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import talib
import copy


def data_wash(data):
    # dataframe数据清洗，如果按时间戳出现重复返回 false 和-1
    # 如果出现最高价最低价错误返回false和错误的行号
    answer = True
    row = 0
    if data.index.is_unique:
        for index in data.index:
            if data.loc[index, 'High'] != max(data.loc[index, 'Open'],
                                              data.loc[index, 'High'],
                                              data.loc[index, 'Low'],
                                              data.loc[index, 'Close']):
                answer = False
                row = index
            elif data.loc[index, 'Low'] != min(data.loc[index, 'Open'],
                                               data.loc[index, 'High'],
                                               data.loc[index, 'Low'],
                                               data.loc[index, 'Close']):
                answer = False
                row = index
            else:
                pass
    else:
        answer = False
        row = -1
    return answer, row


def get_profit(mark, initial_margin):
    # 计算持仓的盯市收益曲线，返回dataframe profit当天收益，total总收益，equity是加上初始资金的权益
    profit = pd.DataFrame(0.0, index=mark.index, columns=['Profit', 'Total', 'Equity'])
    lastclosemark = 0
    lastcloseprice = 0
    lastprofit = 0
    for index in mark.index:
        profit.loc[index, 'Profit'] = ((mark.loc[index, 'OpenPrice'] - lastcloseprice) * lastclosemark +
                                       (mark.loc[index, 'ClosePrice'] - mark.loc[index, 'OpenPrice']) *
                                       mark.loc[index, 'OpenMark'])
        lastclosemark = mark.loc[index, 'CloseMark']
        lastcloseprice = mark.loc[index, 'ClosePrice']
        profit.loc[index, 'Total'] = profit.loc[index, 'Profit'] + lastprofit
        lastprofit = profit.loc[index, 'Total']
    for index in mark.index:
        profit.loc[index, 'Equity'] = profit.loc[index, 'Total'] + initial_margin
    return profit


def static_trades(mark, profit):
    # 交易过程记录，记录整个过程中的开平仓时间，价格和收益
    temp = pd.DataFrame(0.0, index=[0], columns=['Mark', 'OpenDate', 'OpenPrice',
                                                 'CloseDate', 'ClosePrice', 'Profit'])
    begin_mark = 0
    begin_date = 0
    begin_price = 0
    begin_profit = 0
    for index in mark.index:
        if begin_mark == 0 and mark.loc[index, 'OpenMark'] != 0:    # 开始进入持仓状态记录开始时间和价格
            begin_mark = mark.loc[index, 'OpenMark']
            begin_price = mark.loc[index, 'OpenPrice']
            begin_date = index
            begin_profit = profit.loc[index, 'Total'] - profit.loc[index, 'Profit']
            if mark.loc[index, 'CloseMark'] == 0:
                add_line = pd.Series([begin_mark, begin_date, begin_price, begin_date,
                                      mark.loc[index, 'ClosePrice'], profit.loc[index, 'Profit']],
                                     temp.columns)
                temp = temp.append(add_line, ignore_index=True)
                begin_mark = 0
                begin_profit = 0

        elif begin_mark != 0 and mark.loc[index, 'OpenMark'] == 0:    # 结束持仓纪录整个交易
            add_line = pd.Series([begin_mark, begin_date, begin_price, index, mark.loc[index, 'OpenPrice'],
                                  profit.loc[index, 'Total'] - begin_profit], temp.columns)
            temp = temp.append(add_line, ignore_index=True)
            begin_mark = 0
            begin_profit = 0

        elif mark.loc[index, 'OpenMark'] * begin_mark < 0:    # 反手交易拆成2笔
            temp_profit = profit.loc[index, 'Total'] - begin_profit - \
                          (mark.loc[index, 'ClosePrice'] - mark.loc[index, 'OpenPrice']) * mark.loc[index, 'OpenMark']
            add_line = pd.Series([begin_mark, begin_date, begin_price, index,
                                  mark.loc[index, 'OpenPrice'], temp_profit], temp.columns)
            temp = temp.append(add_line, ignore_index=True)
            begin_mark = mark.loc[index, 'OpenMark']
            begin_date = index
            begin_price = mark.loc[index, 'OpenPrice']
            begin_profit = profit.loc[index, 'Total'] - (mark.loc[index, 'ClosePrice'] -
                                                         mark.loc[index, 'OpenPrice']) * mark.loc[index, 'OpenMark']

        else:
            pass

    return temp.drop(0, axis=0)


def cal_vola(data):    
    # 计算波动率。输入为权益序列np.array
    if len(data[data <= 0]) == 0:
        temp = [0] * len(data)
        temp2 = range(len(data))
        for i in temp2:
            temp[i] = data[i]/data[i-1]
        temp[0] = 1
        temp = talib.LN(np.array(temp))
        vola = np.std(temp)
    else:
        vola = -1

    return vola



def linear_normal(data):
    # 计算波动率。输入为权益序列np.array
    for i in range(1, len(data)):
        data[i] = data[i]/data[0]
    data[0] = 1

def linear(data):    
    # 使用线性回归计算年化收益率。输入为np.array输出为斜率（年化收益率）和截距
    linear_normal(data)

    temp = range(len(data))
    work = pd.DataFrame({'x': temp, 'y': data})
    cov = work.y.cov(work.x)
    var = work.var()
    a = cov/var['x']
    mean = work.mean()
    b = mean['y'] - a * mean['x']
    return a*252, b


def cal_maxdd(profit):
    # 计算最大回撤，返回最大回撤数据和开始结束的index
    max_draw_down = 0
    temp_max_value = 0
    begin_index = 0
    end_index = 0
    temp_begin = 0
    for i in range(1, len(profit)):
        if profit[i-1] > temp_max_value:
            temp_max_value = profit[i-1]
            temp_begin = i
        else:
            if 1 - profit[i]/temp_max_value > max_draw_down:
                max_draw_down = 1 - profit[i]/temp_max_value
                begin_index = temp_begin
                end_index = i
            else:
                pass
    return max_draw_down, begin_index, end_index


def cal_maxdt(profit):
    # 计算最长回撤时间，返回周期数和开始结束index
    maxdt = 0
    temp_max_value = 0
    begin_index = 0
    end_index = 0
    temp_begin = 0
    for i in range(1, len(profit)):
        if profit[i-1] > temp_max_value:
            temp_max_value = profit[i-1]
            temp_begin = i
        else:
            if i-temp_begin > maxdt:
                maxdt = i-temp_begin
                begin_index = temp_begin
                end_index = i
            else:
                pass
    return maxdt, begin_index, end_index


def get_static(std, profit):
    # 获取交易的统计值，返回字典
    static = {'CAGR': 0, 'MaxDD': 0, 'MaxDT': 0, 'Vola': 0,
              'WinR': 0, 'PLR': 0, 'Times': 0}
    temp = copy.deepcopy(profit['Equity'].values)
    for i in range(1, len(temp)):
        temp[i] = temp[i]/temp[0]
    temp[0] = 1
    a, b = linear(temp)
    static['CAGR'] = a*252
    temp = copy.deepcopy(profit['Equity'].values)
    static['MaxDD'] = cal_maxdd(temp)[0]
    static['MaxDT'] = cal_maxdt(temp)[0]
    static['Vola'] = cal_vola(temp)*15.8745
    static['Times'] = len(std)
    static['WinR'] = float(len(std.index[std['Profit'] > 0]))/static['Times']
    a = std[std['Profit'] > 0]
    b = std[std['Profit'] < 0]
    static['PLR'] = -a['Profit'].sum()/b['Profit'].sum()
    return static


if __name__ == '__main__':
    data = pd.read_excel('testdata.xlsx', sheetname='data', index_col='Date')
    a = data_wash(data)
    print(a)
