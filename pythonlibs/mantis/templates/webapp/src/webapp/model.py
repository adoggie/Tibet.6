#coding:utf-8

from mantis.fundamental.nosql import model
from mantis.fundamental.nosql.model import Model



class MyModel(Model):
    """定义你的数据模型"""
    def __init__(self):
        Model.__init__(self)
        self.type = "1"
        self.ip = ''
        self.port = 0


# 以下代碼必須保持，在每一個模塊的model中必須複製,以便於支持 Model在不同的數據庫中
var_locals = locals()

def set_database(database):
    model.set_database(var_locals,database)

