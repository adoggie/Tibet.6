#coding:utf-8


from logging import Handler,StreamHandler
from logging.handlers import RotatingFileHandler


class LogHandlerBase(object):
    def __init__(self):
        self.logger = None

    def setLogger(self, logger):
        self.logger = logger


class LogFileHandler(LogHandlerBase,RotatingFileHandler):
    """
    """
    TYPE = 'file'

    def __init__(self, *args, **kwargs):
        RotatingFileHandler.__init__(self, *args, **kwargs)
        LogHandlerBase.__init__(self)

class LogConsoleHandler(LogHandlerBase,StreamHandler):
    """

    """
    TYPE = 'console'

    def __init__(self, *args, **kwargs):
        StreamHandler.__init__(self, *args, **kwargs)
        LogHandlerBase.__init__(self)


