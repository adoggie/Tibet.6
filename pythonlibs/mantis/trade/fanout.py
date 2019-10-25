#coding:utf-8

from mantis.fundamental.application.app import instance

class FanoutSwitcher(object):
    """"""
    def __init__(self,service,cfgs):
        self.cfgs = cfgs
        self.channels = {}
        self.service = service

    def open(self):
        pass

    def close(self):
        pass

    def fanout(self,message,**names):
        for text in self.cfgs.get('channels',''):
            names.update(service_type=self.service.getServiceType(),
                         service_id = self.service.getServiceId())
            text = text.format(**names)
            chan = self.channels.get(text)
            if not chan: # not existed in cache
                brokerName, channelName, type_ = text.split('/')
                broker = instance.messageBrokerManager.get(brokerName)
                chan = broker.createChannel(channelName,type_=type_)
                self.channels[text] = chan
            if chan:
                chan.publish_or_produce(message)
    @property
    def name(self):
        return self.cfgs.get('name')

