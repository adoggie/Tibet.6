#coding:utf-8

from logging import Filter


class LogHandlerFilter(Filter):
    def __init__(self,name,cfg):
        Filter.__init__(self)
        self.name = name
        self.cfg = cfg

    def filter(self,record):
        # text = self.cfg.get('text','')
        tag = self.cfg.get('tag','')
        NO = 0
        YES = 1
        # if record.message.find(text)!=-1 or record.tags.find(tag) != -1:
        # if record.msg.find(text)!=-1 or record.msg.find(tag) != -1:
        if tag and record.msg.find(tag) != -1:
            return YES
        return NO

