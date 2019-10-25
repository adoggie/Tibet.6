#coding:utf-8

import json
from flask import Flask,send_file
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.utils import nocache


@nocache
def index():
    return render_template('main.html')

def orders():
    main = instance.serviceManager.get('main')
    controller = main.controller

    http = instance.serviceManager.get('http')
    http = http.cfgs.get('http')
    host = http.get('host')
    port = http.get('port')
    url = "http://{}:{}/api".format(host,port)
    accounts =[]
    for account in controller.futureHandler.accounts.values():
        accounts.append( {'product':account.product,'account':account.account})
    return render_template('orders.html', http_url = url, accounts=accounts)