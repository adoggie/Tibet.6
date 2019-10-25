#coding:utf-8

import os
import string
import logging


def __FILE__():
    import inspect
    # f = inspect.currentframe().f_back.f_back.f_back
    f = inspect.currentframe().f_back.f_back
    stack = inspect.stack()
    # return f.f_code.co_filename,f.f_lineno
    return stack[3][1],stack[3][2]


class Logger:
    def __init__(self,name):
        self.name = name
        self.logger = logging.getLogger()
        self.fmt_extra = {}
        self.fmt = ''
        self.message_fmt = '' # '%(project_name)s:%(project_version)s %(app_id)s %(_filename)s:%(_lineno)d [%(tags)s] %(message)s'
        self.tags = []
        self.level = logging.INFO

    def setLevel(self,level='INFO'):
        intval = Logger.convertLevelToIntValue(level)
        self.logger.setLevel( intval )
        self.level = intval

    @classmethod
    def convertLevelToIntValue(cls,level):
        maps = {'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL}
        level = string.upper(level)
        intval = maps.get(level, logging.INFO)
        return intval

    def addHandler(self,handler):
        handler.setFormatter(self.fmt)
        self.logger.addHandler(handler)
        # handler.setLogger(self)
        # handler.setLevel(self.level)

    TEMPLATE_FORMAT = '[%(project_name)s:%(project_version)s %(app_id)s] %(levelname)s %(asctime)s %(filename)s:%(lineno)d [%(tags)s] %(message)s'

    def setFormat(self,fmt):
        self.fmt = fmt
        # self.logger
        return self

    # def setMessageFormat(self,fmt):
    #     self.message_fmt = fmt
    #
    # def setFormatExtra(self,extra):
    #     self.fmt_extra = extra
    #     return self


    def setTags(self,tags):
        if type(tags) == str:
            ss = tags.strip()
            if ss:
                tags = ss.split(',')
            else:
                tags = []
        # if type(tags) in (tuple,list):
        self.tags = tags
        return self

    def getTags(self):
        return self.tags

    def addTag(self,tag):
        if self.getTags().count(tag) == 0:
            self.getTags().append(tag)
        return self

    def removeTag(self,tag):
        try:
            self.getTags().remove( tag )
        except:pass


    def _normalize_tags(self,tags):
        ss = ''

        if type(tags) in (tuple, list):
            # tags += self.tags
            tags += self.getTags()
            ss = string.join(map(str, tags), ',')

        if type(tags) == str:
            ss = tags.strip()
            tags=[]
            if ss:
                tags = ss.split(',')
            # tags += self.tags
            tags += self.getTags()
            ss = string.join( map(str,tags),',')
        ss = ss.replace(' ', '_')
        return ss

    def log(self, level, *args, **kwargs):
        self._log(level, *args, **kwargs)

    def _log(self,level,*args,**kwargs):
        """
        """
        # todo. logging bug need for fixing
        text = ''
        for _ in args:
            text += ' ' + str(_)
        self.logger.log( level, text )

        # self.logger.log(level,args[0])

        # self.logger.log(level,args[0],*args[1:])
        # print level,args[0]%args[1:]
        # return
        #
        # if type(level) in (str,unicode):
        #     level = Logger.convertLevelToIntValue(level)
        # extra = self.fmt_extra.copy()
        #
        # # if kwargs.has_key('tags'):
        # #     extra['tags'] = self._normalize_tags( kwargs['tags'])
        # # else:
        # #     extra['tags'] = self._normalize_tags('')
        #
        # extra['tags'] = ''
        #
        # filename,lineno = __FILE__()
        #
        # extra['_filename'] = os.path.basename(filename)
        # extra['_lineno'] = lineno
        # message = self.message_fmt%extra
        #
        # if len(args)>1:
        #     self.logger.log( level ,  message + args[0]%args[1:] )
        # else:
        #     self.logger.log( level ,  message + args[0] )


    def debug(self,*args,**kwargs):
        self._log(logging.DEBUG,*args,**kwargs)
        return self

    def warning(self,*args,**kwargs):
        self._log(logging.WARNING, *args, **kwargs)
        return self

    warn=warning

    def critical(self,*args,**kwargs):
        self._log(logging.CRITICAL, *args, **kwargs)
        return self

    def info(self,*args,**kwargs):
        self._log(logging.INFO, *args, **kwargs)
        return self

    def error(self,*args,**kwargs):
        self._log(logging.ERROR, *args, **kwargs)
        return self

