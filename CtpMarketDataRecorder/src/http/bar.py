# coding: utf-8

import datetime
import time
from flask import request,g
from pymongo import ASCENDING,DESCENDING

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import CR,ErrorReturn
from mantis.trade.errors import ErrorDefs
from mantis.trade.types import  ProductClass , TimeScale
from mantis.trade.config import DatabaseDefs

def query_bars():
    """
    列举所有已订阅的合约代码
    :param symbol
    :param scale
    :param product_class
    :param start :  timestamp 70's
    :param end  : timestamp 70'
    :param limit 查询返回记录最大个数,默认值零表示返回记录不限。
    :return:
    """

    symbol = request.values.get('symbol','')
    if  not symbol:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response

    scale = request.values.get('scale','15m').lower()
    product_class = request.values.get('product_class',ProductClass.Future)
    start = request.values.get('start',0)
    end = request.values.get('end',0)
    limit = request.values.get('limit',500)

    if scale  not in TimeScale.SCALES.keys():
        return ErrorReturn(ErrorDefs.BAR_SCALE_INVALID).response

    service = instance.serviceManager.get('main')
    dbconn = service.datasourceManager.get('mongodb').conn
    dbname = DatabaseDefs.get(product_class,{}).get('bars','').format(scale)
    coll = dbconn[dbname][symbol]

    sortkey = 'datetime'
    dtstart = datetime.datetime.fromtimestamp(int(start))
    dtend = datetime.datetime.fromtimestamp(int(end))
    case = {"datetime":{"$gte":dtstart,"$lte":dtend}}
    if sortkey:
        cursor = coll.find(case).sort(sortkey,ASCENDING)
    else:
        cursor = coll.find(case)
    result = list(cursor.limit(limit))
    for r in result:
        r['datetime'] = time.mktime(r['datetime'].timetuple())
    return CR().assign(result).response
