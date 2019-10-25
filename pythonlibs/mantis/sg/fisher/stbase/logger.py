#coding:utf-8
import copy
import time,datetime
import traceback
import threading
from collections import OrderedDict
from functools import partial
from dateutil.parser import  parse


from order import *

class LogAppender(object):
    def __init__(self):
        pass

    def output(self,text):
        pass

    def init(self,*args,**kwargs):
        pass

    def open(self):
        pass

    def close(self):
        pass

class StdoutLogAppender(LogAppender):
    def __init__(self):
        LogAppender.__init__(self)

    def output(self,text):
        print text

class Logger(object):
    class LEVEL(object):
        DEBUG = 0
        INFO = 1
        WARN = 2
        ERROR = 3
        CRITICAL = 4
        LIST = {DEBUG:'DEBUG',INFO:'INFO',WARN:'WARN',ERROR:'ERROR',CRITICAL:'CRITICAL'}

    def __init__(self):
        self.level = Logger.LEVEL.DEBUG
        self.appenders = []
        self.addAppender(StdoutLogAppender())

    def setLevel(self,level):
        self.level = level

    def format(self,level,text):
        text = '{} {} {}'.format(
            current_datetime_string(),
            Logger.LEVEL.LIST[level],
            text)
        return text

    def addAppender(self,appender):
        self.appenders.append(appender)
        return self

    def open(self):
        pass

    def close(self):
        for _ in self.appenders:
            _.close()
        self.appenders = []

    def output(self,text):
        for _ in self.appenders:
            _.output(text)

    def _print(self,level,text):

        if self.level <= level:
            text = self.format(level,text)
            self.output(text)

    def _format(self,*args,**kwargs):
        text = ''
        for _ in args:
            text += ' ' + str(_)
        for k, v in kwargs.items():
            text += ' ' + str(k) + ': ' + str(v)
        return text

    def debug(self,*args,**kwargs):

        self._print(0, self._format(*args,**kwargs) )
        return self

    def info(self,*args,**kwargs):

        self._print(1,self._format(*args,**kwargs))
        return self

    def warn(self,*args,**kwargs):
        self._print(2,self._format(*args,**kwargs))
        return self

    def error(self,*args,**kwargs):
        self._print(3,self._format(*args,**kwargs))
        return self

    def critical(self,*args,**kwargs):
        self._print(4,self._format(*args,**kwargs))
        return self


class FileLogAppender(LogAppender):
    """文件日志添加"""

    def __init__(self,logfile,dayfile=True,append=True,max_size='64M'):
        LogAppender.__init__(self)
        self.logfile = logfile
        self.cfgs =dict(dayfile=dayfile,append = append,max_size = max_size)
        self.handle = None

    def open(self):
        from controller import TradeController

        mode = 'w'
        if self.cfgs.get('append'):
            mode = 'a+'
        name = '{}_{}.log'.format(self.logfile,current_date_string())
        name = os.path.join(TradeController().getDataPath(),name)
        self.handle = open(name,mode)
        return self

    def output(self,text):
        if not self.handle:
            self.open()
        text = str(text)
        self.handle.write( text + '\n')
        self.handle.flush()
        # print 'FileLogAppender:'+text

    def close(self):
        if self.handle:
            self.handle.close()




class StragetyLoggerAppender(object):
    """策略日志写入基类"""
    def __init__(self):
        self.strategy = None

    def init(self,strategy):
        self.strategy = strategy

    def output(self, data):
        pass

    def open(self):
        pass

    def close(self):
        self.strategy = None

class StragetyLogger(Logger):
    """策略日志类"""
    def __init__(self,strategy):
        self.strategy = strategy
        Logger.__init__(self)
        self.appenders = []
        self.start_time = None

    def onStart(self):
        self.info('Strategy OnStarted')
        self.start_time = datetime.datetime.now()

    def takePosition(self,pos):
        """记录指定合约当前的持仓情况(当前策略)"""
        data = pos.dict()
        data['event'] = 'trace'
        data['code'] = pos.code
        self.output(data)

    def orderRequest(self,req = OrderRequest(code='')):
        """记录下单请求
            req ： OrderRequest
        """
        data = req.dict()
        data['event'] = 'order'
        data['code'] = req.code
        data['text'] = ''
        self.output(data)

    def orderCancel(self,code,order_id):
        """记录下单请求
            req ： OrderRequest
        """
        data = {}
        data['event'] = 'order_cancel'
        data['code'] = code
        data['order_id'] = order_id
        self.output(data)


    def statFunds(self):
        """记录资金状况"""
        data = dict(amount_usable=self.strategy.product.getAmountUsable(),
                    amount_asset = self.strategy.product.getAmountAsset()
                    )
        data['event'] = 'funds'
        data['code'] = ''


    def takeTick(self,tick):
        """记录合约最新tick价格"""
        data = tick.dict()
        data['event'] = 'trace'
        data['code'] = tick.code
        self.output(data)

    def takeBar(self,bar):
        data = bar.dict()
        data['event'] = 'trace'
        data['code']  = bar.code
        self.output(data)

    def takeTradeObject(self,tradeobj):
        data = tradeobj.dict()
        data['event'] = 'trace'
        data['code'] = tradeobj.code
        self.output(data)

    def takeSignal(self,signal):
        """触发买卖信号"""
        data = signal.dict()
        data['event'] = 'signal'
        data['code'] = signal.code
        self.output(data)

    def text(self,code,content='',event='text'):
        data = dict(event=event,code=code,text=content)
        self.output(data)


    def event(self,event,code,text):
        pass

    def _print(self,level,text):
        if self.level <= level:
            text = self.format(level,text)
            data = dict(event='text',text=text)
            self.output( data )

    def output(self,data):
        """ 最终写入
        :param data:  dict{time,event,...}
        :return:
        """
        from controller import TradeController

        data['time'] = datetime.datetime.now()
        data['strategy'] = self.strategy.name
        if not data.has_key('code'):
            data['code'] = ''

        for _ in self.appenders:
            _.output(data)

        # 分派给全局logger对象
        TradeController().getLogger().info(str(data))

    def addAppender(self,appender):
        appender.init(self.strategy)
        self.appenders.append(appender)
        return self

