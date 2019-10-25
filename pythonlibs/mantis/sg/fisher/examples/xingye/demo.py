import sys
import os
import time
import threading
import ctypes

# 创建行情源对象
s = Market.Stk('0601318')
Stk_OrderQty = 0
Stk_pos = 0
B_flag = 0
S_flag = 0
Knockflag = 0
OrigSerailNo_B = []
OrigSerailNo_B = []
ThreadFlag = True


def prodinfo():
    global Stk_OrderQty, Stk_pos
    if Strategy.Product.Stk_UseableAmt > 0:  # 仓位定义：可用资金*10%，固定舍零股处理
        Stk_OrderQty = Stk_OrderQty = int((Strategy.Product.Stk_UseableAmt * 0.1) / stk.KnockPrice) - int(
            (Strategy.Product.Stk_UseableAmt * 0.1) / stk.KnockPrice % 100)

    for pos in Strategy.Product.S_Pos:  # 证券持仓信息：
        if pos.ServerCode == stk.ServerCode:
            Stk_pos = (pos.YdQty + pos.TdQty)


def Knock(OrigSerialNo):
    global ThreadFlag
    try:
        for order in Strategy.GetOrdersByOrigSerialNo(OrigSerialNo):
            if order.StatusCode == 'Fully_Filled':
                return True
            else:
                return False

    except Exception, e:
        ThreadFlag = False
        print 'order error:%s' % str(e)


def Knock_Status():  # 判断单腿成交后，才进行另外一笔委托，如果全部成交，则进行下一个循环
    global OrigSerailNo_B, OrigSerailNo_S, B_flag, S_flag
    if OrigSerailNo_B != [] and OrigSerailNo_S != [] and Knock(OrigSerailNo_S[0]) and Knock(OrigSerailNo_B[0]):
        # 如果买入和卖出委托均全部成交，则初始化参数
        B_flag, S_flag = 0
        OrigSerailNo_B, OrigSerailNo_S = []

    elif B_flag == 1 and OrigSerailNo_B != [] and Knock(OrigSerailNo_B[0]):
        S_flag = 0

    elif S_flag == 1 and OrigSerailNo_S != [] and Knock(OrigSerailNo_S[0]):
        B_flag = 0

    else:
        pass


def Order(stk):
    global OrigSerailNo_B, OrigSerailNo_B, B_flag, S_flag, ThreadFlag
    try:
        while ThreadFlag:

            print '当前涨跌幅stk.DiffRate：%s' % stk.DiffRate
            if stk.DiffRate > 0.01 and Stk_pos >= 0 and S_flag == 0:
                print 'Order_S'

                OrigSerailNo_S = Strategy.Order(OrderItem(stk.ServerCode, 'S', Stk_OrderQty, stk.KnockPrice))
                B_flag, S_flag = 1

            elif stk.DiffRate < -0.01 and Strategy.Product.Stk_UseableAmt > 0 and B_flag == 0:
                print 'Order_B'
                OrigSerailNo_B = Strategy.Order(OrderItem(stk.ServerCode, 'B', Stk_OrderQty, stk.KnockPrice))
                B_flag, S_flag = 1

            else:
                pass
            Knock_Status()
            time.sleep(5)
    except Exception, e:
        ThreadFlag = False
        print 'order error:%s' % str(e)
        Strategy.Exit()


def RtsChanged(items):  # 实时委托回报监控
    global Knockflag
    for rts in items:
        if rts.Type == 0:
            print '收到委托确认：委托号=%s , 代码=%s,委托数量=%i, 委托价格=%i, 状态=%s' % (
            rts.OrigSerialNo, rts.ServerCode, rts.OrderQty, rts.OrderPrice, rts.StatusCode)
        else:
            print '收到成交信息：委托号=%s , 代码=%s,成交数量=%i, 成交价格=%i' % (
            rts.OrigSerialNo, rts.ServerCode, rts.KnockQty, rts.KnockAmt)


def ThreadFlag():  # 释放线程
    global ThreadFlag
    ThreadFlag = False
    print '***Thread End*****'


if __name__ == '__main__':
    Strategy.OnExiting += ThreadFlag
    Strategy.Product.Changed += prodinfo  # 资金、持仓变化后，重新计算委托数量
    t = threading.Thread(target=Order(s))
    t.start()
