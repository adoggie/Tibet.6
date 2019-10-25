#coding:utf-8

import json
from flask import Flask,send_file
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.utils import nocache

@nocache
def ctp_index():
    return render_template('index-ctp.html',profiles = {})