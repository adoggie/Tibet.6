#--coding:utf-8--

import traceback
from datetime import datetime
from logging import getLogger
import socket
import gevent
import gevent.socket
from 	gevent.server import StreamServer
import 	gevent.event
import gevent.ssl

from mantis.fundamental.utils.importutils import import_class
# from mantis.fundamental.application.app import instance

class Logger(object):
	def __init__(self):
		pass

	def debug(self,text):
		print text

	error = debug

logger = Logger()

class Instance(object):

	def getLogger(self):
		return logger

instance = Instance()

class SocketClientIdentifier(object):
	def __init__(self):
		self.unique_id = '' 	# 可以是连接设备的唯一设备标识
		self.props = {}

class ConnectionEventHandler(object):
	"""连接事件接口"""
	def onConnected(self,conn,address):
		pass

	def onDisconnected(self,conn):
		pass

	def onData(self,conn,data):
		pass


class SocketConnection(object):
	def __init__(self,sock=None,consumer=None,server=None):
		self.server = server
		self.sock = sock
		self.consumer = consumer
		self.datetime = None
		self.client_id = SocketClientIdentifier()

	def getAddress(self):
		return 'RpcConnectionSocket:'+str(self.sock.getsockname())

	def open(self):
		self.datetime = datetime.now()
		return True

	def connect(self,host,port):
		self.sock = socket.socket()
		self.sock.connect((host,port))
		self.consumer.onConnected(self,None)

	def close(self):
		if self.sock:
			self.sock.close()
		self.sock = None

	def sendData(self,data):
		# print 'data:',data
		self.sock.sendall(data)
		# instance.getLogger().debug( 'sent >> ' + self.hex_dump(data) )

	def hex_dump(self, bytes):
		dump = ' '.join(map(hex, map(ord, bytes)))
		return dump

	def recv(self):
		while True:
			try:
				d = self.sock.recv(1000)
				if not d:
					break
			except:
				# traceback.print_exc()
				break
			try:
				self.consumer.onData(self,d)
			except:
				instance.getLogger().error(traceback.format_exc())
				# traceback.print_exc()
		instance.getLogger().debug( 'socket disconnected!' )
		self.sock = None

class DataConsumer(object):
	def __init__(self,accumulator,handler):
		self.accumulator = accumulator
		self.handler = handler

	def onData(self,bytes):
		messages = self.accumulator.enqueue(bytes)
		for message in messages:
			self.handler.handle(message)




class Server(object):
	def __init__(self):
		self.cfgs = None
		self.conns = []
		self.server = None

	@property
	def name(self):
		return self.cfgs.get('name')

	def init(self,**kwargs):
		"""
			host :
			port :
			handler: 连接处理器
		"""
		self.cfgs = kwargs
		return self

	def stop(self):
		self.server.stop()

	def start(self):
		ssl = self.cfgs.get('ssl')
		if ssl:
			self.server = StreamServer((self.cfgs.get('host'),self.cfgs.get('port')),
										self._service,keyfile=self.cfgs.get('keyfile'),
				certfile=self.cfgs.get('certfile'))
		else:
			self.server = StreamServer((self.cfgs.get('host'),self.cfgs.get('port')), self._service)

		print 'Socket Server Start On ',self.cfgs.get('host'), ':',self.cfgs.get('port')
		self.server.start() #serve_forever() , not block

	def _service(self,sock,address):
		"""支持 连接处理函数对象 或者 处理对象类型 """
		handler = self.cfgs.get('handler')
		if not handler:
			cls = self.cfgs.get('handler_cls')
			handler = cls()
			kwargs = self.cfgs.get('handler_cls_kwargs',{})
			if kwargs:
				handler.init(**kwargs)

		# handler = cls()

		# consumer = DataConsumer(acc,handler)
		conn = SocketConnection(sock,handler,self)
		self.addConnection(conn)
		# handler.setConnection(conn)
		# handler.setAccumulator(acc)
		handler.onConnected(conn,address)
		conn.recv()
		self.removeConnection(conn)
		handler.onDisconnected(conn)

	def sendMessage(self,m):
		pass

	def addConnection(self,conn):
		self.conns.append(conn)

	def removeConnection(self,conn):
		self.conns.remove(conn)