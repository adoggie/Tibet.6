#coding:utf-8


import base64
from flask import make_response,request,g
from functools import wraps, update_wrapper
from datetime import datetime
from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.BlueEarth.errors import ErrorDefs
from mantis.BlueEarth import model

import json

def login_check(view):
    @wraps(view)
    def _wrapper(*args, **kwargs):
        token = request.headers.get('token')
        auth = token_decode(token)
        if not auth:
            return ErrorReturn(ErrorDefs.TokenIsDirty).response

        user = model.User.get(platform=auth.platform, account=auth.user_id)
        if not user:
            return ErrorReturn(ErrorDefs.UserNotExist).response

        g.auth = auth
        g.user = user
        return view(*args,**kwargs)

    # return update_wrapper(_wrapper, view)
    return _wrapper


def request_log(view):
    @wraps(view)
    def _wrapper(*args, **kwargs):
        auth = g.auth

        return view(*args,**kwargs)

    # return update_wrapper(_wrapper, view)
    return _wrapper



def token_decode(token):
    auth = None
    try:
        data = base64.b64decode(token)
        data = json.loads(data)

        auth = AuthToken()
        object_assign(auth,data)

    except:
        instance.getLogger().warn('Request Token is invalid. Token: {}'.
                                  format(str(token)))
    return auth

def token_encode(data):
    _dict = {}
    if isinstance(data,dict):
        _dict = data
    else:
        _dict  =data.__dict__
    return base64.b64encode(json.dumps(_dict))

def device_token_create(data,secret):
    """添加设备认证成功时的时间戳，并在token传递到其他服务系统时检验token的实效性"""
    from mantis.fundamental.utils.signature import make_signature
    # from mantis.fundamental.utils.timeutils import timestamp_current
    _dict = {}
    if isinstance(data,dict):
        _dict = data
    else:
        _dict  =data.__dict__

    """添加token创建时间，计算所有key/value的摘要，转成 base64"""
    # _dict['auth_time'] = timestamp_current()
    sign,_ = make_signature(secret,_dict)
    _dict['sign'] = sign
    return base64.b64encode(json.dumps(_dict))


def device_token_check( token ,secret):
    from mantis.fundamental.utils.signature import make_signature
    data = None
    try:
        data = json.loads(base64.b64decode(token))
        sign = data['sign']
        del data['sign']
        value,_ = make_signature(secret,data)
        if value != sign:
            data = None
    except:
        data = None
    return data

class AuthToken(object):
    def __init__(self):
        self.login_time = 0
        self.expire_time = 0
        self.user_id = ''
        self.user_name = ''
        self.platform = ''
        self.role = ''
        self.open_id =''

    def encode(self):
        return token_encode(self)

    @staticmethod
    def decode(token):
        auth = token_decode(token)
        return auth