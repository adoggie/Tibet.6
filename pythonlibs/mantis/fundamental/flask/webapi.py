#coding:utf-8

import json as Json
from flask import Response,make_response

from mantis.fundamental.errors import ErrorDefs,ValueEntry

SUCC = 0
ERROR = 1

class CallReturn(object):
    def __init__(self,status=SUCC,errcode=0,errmsg='',result=None):
        self.status = status
        self.errcode = errcode
        self.errmsg = errmsg
        self.result = result

    def assign(self,result):
        self.result = result
        return self

    @property
    def json(self):
        data = {
            'status':self.status,
            'errcode':self.errcode,
            'errmsg':self.errmsg
        }
        errmsg = self.errmsg
        if isinstance(self.errcode,ValueEntry):
            data['errcode'] = self.errcode.value
            if not errmsg:
                errmsg = self.errcode.comment

        data['errmsg'] = errmsg

        if self.result is not None:
            data['result'] = self.result
        return Json.dumps(data)

    @property
    def response(self):
        resp = Response(self.json)
        resp.headers['Content-Type'] = "application/json"
        return resp


def ErrorReturn(errcode,errmsg='',result=None):
    return CallReturn(ERROR,errcode,errmsg,result)

CR = CallReturn
