#coding:utf-8

__doc__=u'zkclient '
"""
https://kazoo.readthedocs.io/en/latest/basic_usage.html

"""
import os.path
from kazoo.client import KazooClient
import logging
logging.basicConfig()

class ZKClient(object):
    def __init__(self,cfg):
        self.cfg = cfg
        self.zk = None
        self.root = cfg.get('root','/')

    def open(self):
        self.zk = KazooClient(hosts=self.cfg.get('hosts',''))
        self.zk.start()


    def onWatch(self,ev):
        pass

    def getNodeData(self,node,default=None):
        data = default
        node = os.path.join(self.root,node)
        if self.zk.exists(node):
            data,stat = self.zk.get(node)
        return data

    def setNodeData(self,node,data):
        node = os.path.join(self.root, node)
        self.zk.ensure_path(node)
        self.zk.set(node,data)

    def createNode(self,node):
        node = os.path.join(self.root, node)
        self.zk.ensure_path(node)
        # self.zk.create(node)

    def removeNode(self,node,recursive=True):
        node = os.path.join(self.root, node)
        self.zk.delete(node,recursive)

    def setRootNode(self,node):
        self.root = node

    @property
    def handler(self):
        return self.zk

    def getChildren(self,root=None):
        if not root:
            root = self.root
        return self.zk.get_children(root)

