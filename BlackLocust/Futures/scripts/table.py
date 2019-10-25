#coding:utf-8
from collections import OrderedDict

STOP_WIN = 23  # 止盈止损 窗口日
STOP_WIN_MIN = 14
N = 1
TIMEPERIOD = 24

predefines ={
    'STOP_WIN':{'low':10,'high':60,'step':2},
    'STOP_WIN_MIN':{'low':5,'high':40,'step':2},
    'TIMEPERIOD':{'low':10,'high':80,'step':2},
    'N': {'low':0.5,'high':3,'step':.1}
}


predefines ={
    'STOP_WIN':{'low':10,'high':60,'step':3},
    'STOP_WIN_MIN':{'low':5,'high':40,'step':3},
    'TIMEPERIOD':{'low':10,'high':80,'step':3},
    'N': {'low':0.5,'high':3,'step':.1}
}

Tables = []

def _make_table(cfgs={}):
    """生成参数表"""
    predefines.update(cfgs)
    ps =predefines['STOP_WIN']
    for sw in range( ps['low'],ps['high']+ps['step'],ps['step']):
        ps2 = predefines['STOP_WIN_MIN']
        for swm in range( ps2['low'] ,ps2['high']+ps2['step'],ps2['step']):
            # swm  = min(swm,sw ) # must STOP_WIN_MIN < STOP_WIN
            if swm >= sw:
                continue
            ps3 = predefines['TIMEPERIOD']
            for tp in range(ps3['low'],ps3['high']+ps3['step'],ps3['step']):
                item = OrderedDict(stop_win = sw,stop_win_min= swm, timeperiod = tp, n = 1)
                Tables.append( item )
    # return [dict(stop_win = 10,stop_win_min= 5, timeperiod = 10, n = 1)]
    return Tables

def make_table(cfgs={}):
    """生成参数表"""
    import numpy as np
    predefines.update(cfgs)
    ps =predefines['STOP_WIN']
    for sw in range( ps['low'],ps['high']+ps['step'],ps['step']):
        ps2 = predefines['STOP_WIN_MIN']
        for swm in range( ps2['low'] ,ps2['high']+ps2['step'],ps2['step']):
            # swm  = min(swm,sw ) # must STOP_WIN_MIN < STOP_WIN
            if swm >= sw:
                continue
            ps3 = predefines['TIMEPERIOD']
            for tp in range(ps3['low'],ps3['high']+ps3['step'],ps3['step']):
                ps4 = predefines['N']
                for n in np.arange(ps4['low'], ps4['high']+ps4['step'], ps4['step'])[:-1]:
                    item = OrderedDict(stop_win = sw,stop_win_min= swm, timeperiod = tp, n = n)
                    Tables.append( item )

    # return [dict(stop_win = 10,stop_win_min= 5, timeperiod = 10, n = 1)]
    return Tables

def write_file():
    f = open('run_params.txt','w')
    for e in Tables:
        s = [  " {}:{} ".format( n, e[n]) for n in e.keys() ]
        f.write(''.join(s)+'\n')
    f.close()

if __name__ == '__main__':
    make_table()
    write_file()