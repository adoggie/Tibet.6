#coding:utf-8

from mantis.fundamental.application.app import  instance

def get_redis(name=None):
    p = instance.getPlugins('redis')[0]
    if not name:
        return p.getElement()
    return p.getElement(name)

def get_mongodb(name=None):
    p = instance.getPlugins('mongodb')[0]
    return p.getElement()

def get_qpid_queue(name=None):
    p = instance.getPlugins('qpid')[0]
    return p.getElement(name)

def get_kafka_topic(name=None):
    p = instance.getPlugins('kafka')[0]
    return p.getElement(name)

def get_flask():
    p = instance.getPlugins('flask')[0]
    return p




