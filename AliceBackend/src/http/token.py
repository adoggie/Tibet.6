#coding:utf-8


import base64
from flask import make_response,request,g
from functools import wraps, update_wrapper
from datetime import datetime
from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.utils.useful import hash_object,object_assign
from mantis.fanbei.smartvision.errors import ErrorDefs
from mantis.fanbei.smartvision import model


import json

def login_check(view):
    @wraps(view)
    def _wrapper(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            token = request.values.get('token')
        auth = token_decode(token)
        if not auth:
            return ErrorReturn(ErrorDefs.TokenInvalid).response

        # user = model.User.get(platform=auth.platform, account=auth.user_id)
        # if not user:
        #     return ErrorReturn(ErrorDefs.UserNotExist).response

        g.auth = auth
        # g.user = user
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
        return data
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
