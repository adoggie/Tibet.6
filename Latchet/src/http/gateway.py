# coding: utf-8

import traceback
from collections import OrderedDict
from flask import request,g,Response
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.flask.webapi import CR
from mantis.fundamental.utils.importutils import import_class

http = instance.serviceManager.get('http')
main = instance.serviceManager.get('main')
app = http.getFlaskApp()


@app.route('/socket.io/<path:remaining>')
def stream_gateway(remaining):
    """
    列举所有已订阅的合约代码
    :return:
    """
    try:
        instance.setProps(SubscribeTable=SubscribeTable())
        channel_defs = {}
        for channel in main.getConfig().get('gateway',[]):
            name = channel.get('name')
            cls = import_class(channel.get('class'))
            channel_defs[name] = cls

        socketio_manage(request.environ, channel_defs, request)
    except:
        traceback.print_exc()
        # app.logger.error("Exception while handling socketio connection",exc_info=True)
    return Response()

class SubscribeChannel(BaseNamespace):
    """
    定义一种消息订阅的通道对象 ， 需在 setttings.main.gateway中指定
    """
    def initialize(self):
        # instance.setProps(quote_mall=self)
        self.logger = instance.getLogger()
        self.event = 'data'
        for ch_cfg in main.getConfig().get('gateway'):
            if self.ns_name == ch_cfg.get('name'):
                self.event = ch_cfg.get('event')

        # main.registerTimedTask(self.time_action,timeout =1)

    def time_action(self,timer):
        # self.onTick('ABC',{'name':'scott'})
        pass 

    def recv_connect(self):
        self.log('client come in..')
        # self.join('ctp')

    def recv_disconnect(self):
        # print self.socket
        self.log('client disconnected..')
        SubscribeTable().discard_all_subs(self)
        BaseNamespace.recv_disconnect(self)

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_subscribe(self, topic):
        self.log('subscribe symbol: ' + topic)
        SubscribeTable().subscribe(topic,self)
        return True

    def on_unsubscribe(self,topic):
        self.log('unsubscribe symbols:'+topic)
        SubscribeTable().unsubscribe(topic,self)
        return True

@singleton
class SubscribeTable(object):
    def __init__(self):
        self.topic_list = OrderedDict()

    def subscribe(self,topic,channel):
        topic = channel.ns_name+'_'+topic
        if topic not in self.topic_list:
            self.topic_list[topic] = set()
        self.topic_list[topic].add(channel)

    def unsubscribe(self,topic,channel):
        topic = channel.ns_name + '_' + topic
        nss = self.topic_list.get(topic,set())
        if channel in nss:
            nss.remove(channel)

    def discard_all_subs(self,channel):
        for nss in self.topic_list.values():
            print 'nss:',nss
            if channel in nss:
                nss.remove(channel)

    def emit_message(self, ns_name,topic, data):
        """This is sent to all in the room (in this particular Namespace)"""
        _topic = ns_name + '_' + topic
        nss = self.topic_list.get(_topic,{})
        for ns in nss:
            event = ns.event
            pkt = dict(type="event",
                       name=event,
                       args= (topic,data),
                       endpoint=ns.ns_name)
            socket = ns.socket
            socket.send_packet(pkt)


    def onTick(self,symbol, tickobj):
        try:
            data = tickobj.__dict__
            del data['datetime']
            self.emit_message(symbol,data)
            # self.broadcast_event('data',symbol,data)
        except:
            traceback.print_exc()