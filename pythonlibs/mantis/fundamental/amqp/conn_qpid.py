#coding:utf-8

__author__=u'sam '

"""
conn_qpid.py

2017/07/07  sam
  1. 消息接收处理增加异常保护，防止异常抛出导致接收终止
     消息处理之后进行确认，保证消息不丢失，异常产生重新接收

"""

from threading import Condition
from threading import Lock
from threading import Thread
import traceback
import gevent

from qpid.messaging import Connection
from qpid.messaging import Message
# from qpid.util import URL
from camel.fundamental.amqp.base import MessageQueueType,AccessMode
from camel.fundamental.utils.importutils import import_function
from camel.biz.application.camelsrv import CamelApplication,instance


class MQConnectionQpid(object):
    def __init__(self,cfg):
        self.type  = MessageQueueType.QPID
        self.name = cfg.get('name')
        self.host = cfg.get('host')
        self.port = cfg.get('port')
        self.address = cfg.get('address')
        self.execthread_nr = cfg.get('exec_thread_nr',1)
        self.entry = cfg.get('entry')

        self.conn = None
        self.ssn = None

        self.producer = None
        self.consumer = None
        self.cond_readable = Condition()
        self.thread = None
        self.isclosed = True
        self.execthreads = []
        self.message_pool = []
        self.lock = Lock()

        self.func_list ={} #导入的函数列表
        self.rw = 0


    def open(self,access=AccessMode.READ):
        if access == 0:
            return self

        broker = "%s:%s" % (self.host, self.port)
        # if self.conn is not None:
        #     return self
        if not self.conn:
            self.conn = Connection(broker, reconnect=True, tcp_nodelay=True)
            self.conn.open()
            self.ssn = self.conn.session()

        if access & AccessMode.READ:
            if not self.consumer:
                self.consumer = self.ssn.receiver(self.address)
                self.consumer.capacity = 4000

                func = import_function(self.entry)  # importing functions dynamically
                self.func_list[self.entry] = func

                self.thread = Thread(target=self._messageRecieving)
                self.thread.start()

        if access & AccessMode.WRITE:
            if not self.producer:
                self.producer = self.ssn.sender(self.address)

        return self

    def close(self):
        self.isclosed = True
        with self.cond_readable:
            self.cond_readable.notify_all()
        if self.conn :
            self.conn.close()
            self.conn = None
        self.thread.join()

    def _executeThread(self):
        """多线程"""
        while not self.isclosed:
            with self.cond_readable:
                self.cond_readable.wait()
            if self.isclosed:
                break
            message = None
            self.lock.acquire()
            if len(self.message_pool):
                message = self.message_pool[0]
                del self.message_pool[0]
            self.lock.release()

            if message is not None:
                func = self.func_list[self.entry]
                func(message) # pass into user space
        print 'topic read thread is exiting..'

    def produce(self,message):
        message = Message(message)
        self.producer.send(message, False)

    def _messageRecieving(self):
        """消息接收线程,保证一个线程接收"""
        self.isclosed = False
        for nr in range(self.execthread_nr):
            thread = Thread(target=self._executeThread)
            self.execthreads.append(thread)
            thread.start()

        while not self.isclosed:
            try:
                message = self.consumer.fetch()
                message = message.content
                # self.ssn.acknowledge(sync=False)
                if message is not None:
                    func = self.func_list[self.entry]
                    try:
                        func(message)
                        self.ssn.acknowledge(sync=False)
                    except:
                        instance.getLogger().error(u'amqp::qpid message process error. detail:{}'.format(traceback.format_exc()))
                    # self.lock.acquire()
                    # self.message_pool.append(message)
                    # self.lock.release()
                    # with self.cond_readable:
                    #     # self.cond_readable.notify()
                    #     self.cond_readable.notify_all()
            except:
                instance.getLogger().warn(u'amqp::qpid fetch message failed. detail:{}'.format(traceback.format_exc()))
                gevent.sleep(5)

        # for thread in self.execthreads:
        #     thread.join()
        instance.getLogger().info( 'amqp::qpid recieve-thread is exiting...')


__all__ = (MQConnectionQpid)