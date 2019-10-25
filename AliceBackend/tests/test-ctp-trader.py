#coding:utf-8


import time,os,sys,datetime,traceback
import requests

url = 'http://192.168.1.252:17001/ctp/order/cancel'
res = requests.post(url,data=dict(order_id='A#17#-360297775#2'))
print res.text
