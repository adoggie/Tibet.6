#coding:utf-8
"""
st_sim.py
行情和交易模拟

"""
import os,os.path
import time
import json
import traceback
import stbase
from threading import  Thread,Timer

class FileGenerator(stbase.MarketGenerator):
    """历史行情数据生成器"""
    def __init__(self,market):
        stbase.MarketGenerator.__init__(self)
        self.thread = Thread(target=self.readThread)
        self.stopped = True
        self.market = market

    def init(self,*args,**kwargs):
        """从指定文件中读取并播放tick和bar数据
            path : 行情数据的目录
            ticks : ['a.tick','b.tick',..]
            bars: ['a.bar','b.bar',..]

        """
        self.path= kwargs.get('path')
        self.ticks = kwargs.get('ticks',[])
        self.bars = kwargs.get('bars',[])

        return self

    def open(self):
        pass

    def close(self):
        pass

    def readThread(self):
        self.stopped = False

        # read ticks
        for name in self.ticks:
            path = os.path.join(self.path,name)
            fp = open(path)
            lines = fp.readlines()
            lines = map(str.strip,lines)
            lines = filter(lambda _:_[0]!='#',lines)
            fp.close()
            for line in lines:
                if self.stopped:
                    return
                jsondata = json.loads(line)
                tick = stbase.TickData(jsondata)
                self.market.putData(tick)

        # read bars
        for name in self.ticks:
            path = os.path.join(self.path, name)
            fp = open(path)
            lines = fp.readlines()
            lines = map(str.strip, lines)
            lines = filter(lambda _: _[0] != '#', lines)
            fp.close()
            for line in lines:
                if self.stopped:
                    return
                jsondata = json.loads(line)
                tick = stbase.TickData(jsondata)
                self.market.putData(tick)


