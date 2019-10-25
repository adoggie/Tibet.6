#coding:utf-8


from logging import Handler
from camel.fundamental.logging.handler import LogHandlerBase

class LogtailHander(LogHandlerBase,Handler):
    def __init__(self,*args,**kwargs):
        Handler.__init__(self,*args,**kwargs)
        LogHandlerBase.__init__(self)

    def emit(self, record):
        pass

    def flush(self):
        pass

    def close(self):
        pass

#
#
# class LogHandlerMixer(object):
#     def _initLogHandler(self, cfg):
#         #新的handler添加请放在此处初始化
#         from camel.fundamental.application import Application
#         return Application._initLogHandler(self, cfg)