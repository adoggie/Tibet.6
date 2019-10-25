#coding:utf-8

from camel.fundamental.logging.logger import Logger


class FlaskHttpRequestLogger(Logger):
    """将日志中的Tags项关联到 flask的request对象中
    """
    def __init__(self,*args,**kwargs):
        Logger.__init__(self,*args,**kwargs)

    def setTags(self,tags):
        from flask import request,g
        if type(tags) == str:
            ss = tags.strip()
            if ss:
                tags = ss.split(',')
            else:
                tags = []
        # if type(tags) in (tuple,list):
        g.log_tags = tags
        return self

    def getTags(self):
        from flask import request,g
        if not hasattr(g,'log_tags'):
            g.log_tags = []
        return g.log_tags


