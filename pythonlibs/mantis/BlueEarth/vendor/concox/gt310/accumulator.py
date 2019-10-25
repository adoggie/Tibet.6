#coding:utf-8

from protocal import *
from packet import NetWorkPacket
import message
from mantis.BlueEarth.vendor.concox.gt03.accumulator import DataAccumulator as DataAccumulator_

class DataAccumulator(DataAccumulator_):
    def __init__(self):
        DataAccumulator_.__init__(self,NetWorkPacket)





