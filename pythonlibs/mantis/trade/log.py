# coding: utf-8

import time
from logging import Handler
import logging
from mantis.fundamental.logging.handler import LogHandlerBase
from mantis.fundamental.logging.logger import Logger
from mantis.fundamental.application.app import instance

# class TradeServiceLogger(Logger):
#     def __init__(self,service):
#         name = "%s.%s"%(service.getServiceType(),service.getServiceId())
#         Logger.__init__(self,name)
#         self.service = service
#         self.channels =[]
#         cfgs = self.service.getConfig()
#         for dest in cfgs.get('logging',[]):
#             broker,channel,type_ = dest.get('name').split('/')
#             channel = channel.format(service_type = service.getServiceType(),
#                                      service_id = service.getServiceId())
#             brokerObj = instance.messageBrokerManager.get(broker)
#             chanObj = brokerObj.createChannel(channel,type_)
#             self.channels.append(chanObj)


class TradeServiceLogHandler(LogHandlerBase,Handler):
    """
    """
    TYPE = 'tradelogger'

    def __init__(self, service,item='logging'):
        Handler.__init__(self)
        LogHandlerBase.__init__(self)
        self.service = service
        self.item = item


    def emit(self,record):
        msg = self.format(record)
        self.service.dataFanout(self.item,msg)

class StrategyLogHandler(object):
    """
    策略日志处理器
    一个策略运行涉及多个服务，将多个服务的日志收集到一致的日志输出，这里将日志封装成统一的消息，
    并被发送的queue和pubsub中，以供其他进程收集日志和消费日志
    """
    TYPE = 'strategylogger'

    def __init__(self, strategy_id,service,default_logger=None,item='strategy_logging'):
        self.strategy_id = strategy_id
        self.service = service
        self.item = item
        self.default_logger = default_logger # 策略消息被回路到系统logger中去记录

    def _log(self,level,*args,**kwargs):
        from command import StrategyLogContent
        from message import Message
        log = StrategyLogContent()
        log.level = level
        log.timestamp = int(time.time())
        log.strategy_id = self.strategy_id
        log.service_id = self.service.service_id
        log.service_type = str(self.service.service_type)
        log.text = u' '.join(*args)
        msg = Message(StrategyLogContent.NAME,data=log.__dict__)
        self.service.dataFanout(self.item,msg.marshall(),strategy_id=self.strategy_id)
        # fanout 配置项目中可以设置 {strategy_id}占位变量

        if self.default_logger: # 回路到系统服务日志
            self.default_logger.log(level,*args,**kwargs)

    def debug(self, *args, **kwargs):
        self._log(logging.DEBUG, *args, **kwargs)
        return self

    def warning(self, *args, **kwargs):
        self._log(logging.WARNING, *args, **kwargs)
        return self

    warn = warning

    def critical(self, *args, **kwargs):
        self._log(logging.CRITICAL, *args, **kwargs)
        return self

    def info(self, *args, **kwargs):
        self._log(logging.INFO, *args, **kwargs)
        return self

    def error(self, *args, **kwargs):
        self._log(logging.ERROR, *args, **kwargs)
        return self



__all__ = ( TradeServiceLogHandler,StrategyLogHandler)