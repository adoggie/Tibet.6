#coding:utf-8

import datetime

from mantis.fundamental.utils.timeutils import datetime_to_str

from collections import OrderedDict


def normal_dict(document):
    if document.has_key('_id'):
        del document['_id']

    dict = OrderedDict()
    for k,v in document.items():
        if isinstance(v,(int,float,str,unicode,bool)):
            dict[k] = v
        elif isinstance(v,datetime.datetime):
            dict[k] = datetime_to_str(v)
    return dict