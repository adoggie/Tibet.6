#coding:utf-8

import time ,datetime
from dateutil.parser import  parse

class Stocks(object):
    @staticmethod
    def in_trading_time(dt= None):
        if not dt:
            dt = datetime.datetime.now()

        tm = dt.time()

        a = datetime.time(9,30)
        b = datetime.time(11,30)
        c = datetime.time(13,1)
        d = datetime.time(15,0)

        if (a <= tm and tm <= b ) or ( c <= tm  and tm<= d):
            return True
        return False


def get_trade_database_name(dbname = 'TradeFisher',date = None):

    if date:
        date = parse(date)
    else:
        date = datetime.datetime.now()

    dbname = dbname + '_{}-{}-{}'.format(date.year,date.month,date.day)
    return dbname