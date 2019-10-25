#coding:utf-8


"""
stgenerator.py
回测生成行情数据

"""

import time
import datetime
import ams
import stbase
from dateutil.parser import parse
import pandas as pd
import numpy as np

from mantis.sg.fisher.utils.useful import object_assign


from mantis.sg.fisher.tools import tdx_quote

class MarketGeneratorTDXBar(stbase.MarketGenerator):
	"""文件行情生成器, 通达信k线文件"""

	def __init__(self):
		stbase.MarketGenerator.__init__(self)
		self.cfgs = dict(async_send=True,wait_sec=0,quote_file='')
		self.bars =[]


	def init(self,*args,**kwargs):
		"""
		kwargs:
			code 证券代码
			quote_file 行情记录文件
			ktype   k线类型 5,15,30,60 D
			play_start	回放开始时间
			play_end	回放开始时间

		tdx 行情导出的文件 [0,1,-1] 三行不做使用
		 format of tdx export file :
		 	"yyyy-mm-dd,hhmm,open,high,low,close,vol,amount"
		"""
		self.cfgs.update(kwargs)

		bars = tdx_quote.loadQuoteBars(self.cfgs.get('quote_file'),ktype=self.cfgs.get('ktype'))
		self.bars = bars
		return self

	def open(self):
		"""开始播放"""
		st = parse(self.cfgs.get('play_start'))
		et = None
		if self.cfgs.get('play_end'):
			et = parse(self.cfgs.get('play_end'))
		if not et:
			et = datetime.datetime.now()

		for bar in self.bars:
			if bar.time < st or bar.time > et:
				continue

			if self.cfgs.get('wait_sec'):
				time.sleep(self.cfgs.get('wait_sec'))

			if self.market:
				if self.cfgs.get('async_send'):
					self.market.putData(bar)
				else:
						self.market.onBar(bar)
			else:
				print bar.dict()

	def getHistoryBars(self,code, cycle, limit=100, now=None):
		"""
		获取历史k线记录 ,ktype 必须是 tdx 文件的k线类型

		cycle:  k线周期类型
		limit:  最大返回记录
		now :  运行当前时间,  dataset[now-limit:now]

		"""
		# if not ktype:
		# 	print 'Error: cycle({}) not match in getHistoryBars()'.format(cycle)
		# 	return []
		bars = []
		for n in range(len(self.bars)):
			bar = self.bars[n]
			if bar.time == now: # 定位到当前运行触发的bar
				bars = self.bars[n-limit:n+1]
				break
		if not bars:
			bars = self.bars
		return bars

class MarketGeneratorTDXTick(stbase.MarketGenerator):
	"""行情分时Tick记录生成器, 读取通达信分时导出文件"""

	def __init__(self):
		stbase.MarketGenerator.__init__(self)
		self.cfgs = dict(async_send=True,wait_sec=0,src_file='')

	def init(self,*args,**kwargs):
		self.cfgs.update(kwargs)

		return self

	def open(self):
		"""开始播放"""
		objects = []
		for _ in objects:
			if self.cfgs.get('wait_sec'):
				time.sleep(self.cfgs.get('wait_sec'))
			if self.cfgs.get('async_send'):
				self.market.putData(_)
			else:
				if isinstance(_,stbase.TickData):
					self.market.onTick(_)
				elif isinstance(_,stbase.BarData):
					self.market.onBar(_)


class MarketGeneratorTushare(stbase.MarketGenerator):
	"""文件行情生成器, Tushare 数据源"""

	def __init__(self):
		stbase.MarketGenerator.__init__(self)
		self.cfgs = dict(async_send=True,wait_sec=0,src_file='')
		# aysnc_send : 读取的tick/bar 推送到queue或者直接调用 onTick/onBar
		# wait_sec :  每项行情记录发送的间隔
		# self.dataset = []
		self.df = None

	def init(self,*args,**kwargs):
		"""
		kwargs:
			- code  证券代码
			- data_start  开始时间
			- data_end 	结束时间
			- ktype 	k线类型  5,15,30,60 D
			- play_start	回放开始时间
			- play_end	回放开始时间

		加载历史k线数据
		"""
		import tushare as ts

		self.cfgs.update(kwargs)

		ktype = 'D'
		if self.cfgs.get('ktype'):
			ktype = self.cfgs.get('ktype')
		df = ts.get_hist_data(self.cfgs.get('code'), start=self.cfgs.get('data_start'),
							   ktype=ktype)
		df = df.sort_index()

		# df.index = df.index.to_datetime()


		self.df = df
		return self

	def open(self):
		"""加载历史行情，开始播放"""
		df = self.df

		st = self.cfgs.get('play_start')
		et = self.cfgs.get('play_end')

		# 过滤回放时间段的记录
		df = df[st:et]

		rows = zip(df.index, df.close)
		# for time_,close in rows.items():
		for _ in rows:
			time_,close = _
			bar = stbase.BarData()
			bar.code = self.cfgs.get('code')
			bar.time = parse(time_)
			bar.close = close

			if self.cfgs.get('wait_sec'):
				time.sleep(self.cfgs.get('wait_sec'))
			if self.market:

				if self.cfgs.get('async_send'):	# 异步发送推入 market的接收队列
					self.market.putData(bar)
				else: # 否则直接调用 行情 处罚处理接口
					self.market.onBar(bar)
			else:
				print bar.dict()

	def getHistoryBars(self,code, cycle, limit, now=None):
		"""
		获取历史k线记录

		cycle:  k线周期类型
		limit:  最大返回记录
		now :  当前时间,  dataset[now-limit:now]

		:return:
		"""
		kmap = {
			'5m':'5',
			'15m':'15',
			'30m':'30',
			'60m':'60',
			'd':'D'

		}
		ktype = kmap.get(cycle)
		if not ktype:
			print 'Error: cycle({}) not match in getHistoryBars()'.format(cycle)
			return []
		result = []

		# 帅选出 指定时间 now 之前的 limit根 k线
		df = self.df[:now]
		print len(df)

		for time,close in df.close.to_dict().items():
			bar = stbase.BarData()
			bar.code = self.cfgs.get('code')
			bar.cycle = ktype
			bar.time = time
			bar.close = close
			result.append(bar)
		return result


class MarketGeneratorMongoDBBar(stbase.MarketGenerator):
	"""文件行情生成器,mongodb中读取行情记录"""

	def __init__(self):
		stbase.MarketGenerator.__init__(self)
		self.cfgs = dict(async_send=True,wait_sec=0,quote_file='')
		self.bars =[]
		self.conn = None
		self.db = None
		self.onStart = None
		self.onEnd = None


	def init(self,*args,**kwargs):
		"""
		kwargs:
			host  	主机ip
			port	主机端口
			user
			password
			db		数据库名称

			code 证券代码
			ktype   k线类型 , '' : tick数据
			play_start	回放开始时间
			play_end	回放开始时间

		"""
		from pymongo import MongoClient
		self.cfgs.update(kwargs)

		host = '127.0.0.1'
		port = 27017
		dbname = self.cfgs.get('db')
		if self.cfgs.get('host'):
			host = self.cfgs.get('host')
		if self.cfgs.get('port'):
			port = self.cfgs.get('port')

		conn = MongoClient(host, port)
		self.conn = conn
		self.db = conn[dbname]

		# bars = tdx_quote.loadQuoteBars(self.cfgs.get('quote_file'),ktype=self.cfgs.get('ktype'))
		# self.bars = bars
		return self

	def open(self):
		"""开始播放"""


		st = self.cfgs.get('play_start')
		if not st:
			st = datetime.datetime.now()
			st = st.replace(hour=9,minute=20,second=0)
		else:
			st = parse(self.cfgs.get('play_start'))

		et = None
		if self.cfgs.get('play_end'):
			et = parse(self.cfgs.get('play_end'))
		if not et:
			et = datetime.datetime.now()
			et = et.replace(hour=15,minute=20,second=0)

		if self.cfgs.get('ktype'):
			collname = '{}_{}'.format(self.cfgs.get('code'), self.cfgs.get('ktype'))
		else: # tick 数据
			collname = self.cfgs.get('code')

		coll = self.db[collname]
		rs = coll.find({'time': {'$gte':st,'$lte':et}}).sort('time',1)
		rs = list(rs)

		if self.onStart:
			self.onStart()
		# rs.append({})
		for r in rs:
			if self.cfgs.get('ktype'):
				data = stbase.BarData()
			else:
				data = stbase.TickData()

			# object_assign(data,r)
			data.assign(r)
			# if not data.code:
			# 	print data
			if self.cfgs.get('wait_sec'):
				time.sleep(self.cfgs.get('wait_sec'))

			if self.market:
				if self.cfgs.get('async_send'):
					self.market.putData(data)
				else:
					if self.cfgs.get('ktype'):
						self.market.onBar(data)
					else:
						self.market.onTick(data)
			else:
				print data.dict()

		if self.onEnd:
			self.onEnd()

	def getHistoryBars(self,code, cycle, limit=100, now=None):
		"""
		获取历史k线记录 ,ktype 必须是 tdx 文件的k线类型

		cycle:  k线周期类型
		limit:  最大返回记录
		now :  运行当前时间,  dataset[now-limit:now]

		"""
		# if not ktype:
		# 	print 'Error: cycle({}) not match in getHistoryBars()'.format(cycle)
		# 	return []
		bars = []
		for n in range(len(self.bars)):
			bar = self.bars[n]
			if bar.time == now: # 定位到当前运行触发的bar
				bars = self.bars[n-limit:n+1]
				break
		if not bars:
			bars = self.bars
		return bars


if __name__ == '__main__':
	# generator = MarketGeneratorTushare().init(code='600848', wait_sec=1, data_start='2018-12-04',
	# 			play_start='2018-12-10', play_end='2018-12-21',ktype='5')

	# 通达信数据读取
	# quote_file = '/root/Desktop/Projects/Branches/mantis/sg/fisher/tests/tdx-data/SH#600000-5.txt'
	quote_file = './tests/tdx-data/SH#600000-5.txt'
	generator_tdx = MarketGeneratorTDXBar().init(code='600000', wait_sec=.1, quote_file=quote_file,
												 play_start='2018-12-10', play_end='2018-12-21', ktype='5')


	generator_tdx.open()



