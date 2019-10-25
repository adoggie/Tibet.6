#coding:utf-8


from dateutil.parser import parse
from mantis.sg.fisher import stbase

def loadQuoteBars(quote_file,code='',ktype='5m'):
    """
    加哉行情数据
    :param quote_file:
    :param ktype:
    :return:
    """
    bars = []
    lines = open(quote_file).readlines()
    lines = map(str.strip, lines)
    if not code:
        code = lines[0].split(' ')[0]
    lines = lines[2:-1]
    for line in lines:
        fs = line.split(',')
        ymd, hm, open_, high, low, close, vol, amount = fs[:8]
        dt = ymd + ' ' + hm[:2] + ':' + hm[2:] + ':00'
        bar = stbase.BarData()
        bar.code = code
        bar.cycle = ktype
        bar.open = float(open_)
        bar.high = float(high)
        bar.low = float(low)
        bar.close = float(low)
        bar.vol = float(vol)
        bar.amount = float(amount)
        bar.time = parse(dt)
        bars.append(bar)
    return bars

def importQuoteBarsIntoMongoDB(conn,quote_file,code='',ktype='5m'):
    pass