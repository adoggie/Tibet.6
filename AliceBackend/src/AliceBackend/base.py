#coding:utf-8

class SystemDeviceType(object):
    InnerBox = 1        # 主屏分离的室内主机
    InnerScreen = 2     # 主屏分离的室内屏
    OuterBox = 3        # 室外机
    PropCallApp = 4     # 物业值守
    PropSentryApp = 5   # 物业岗亭机
    Others = 10

    ValidatedList = (1,2,3,4,5)


class Constants(object):
    SUPER_ACCESS_TOKEN = 'YTU3NzVlYjktYjQwMi00MGY2LTkxZjktYWMxYjIxZjM4NjNlCg =='