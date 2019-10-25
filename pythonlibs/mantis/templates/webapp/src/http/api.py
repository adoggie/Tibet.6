#coding:utf-8

import json
import time
import datetime
import os.path
import os
from collections import OrderedDict
from flask import Flask,request,g
from flask import Response
import requests
import base64
from StringIO import StringIO

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.utils.useful import cleaned_json_data


from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import current_datetime_string,timestamp_current,timestamp_to_str
from token import token_encode
from token import  login_check


def hello():
    """写下第一个webapi """
    ip= request.remote_addr
    result = []
    return CR(result = result)

