#coding:utf-8


class YamlConfigParser:
	def __init__(self,conf):
		self.props ={}
		self.conf = conf
		self.loadFile(conf)

	def loadFile(self,conf):
		import yaml
		f = open(conf)
		self.props = yaml.load(f.read())
		f.close()

