#coding:utf-8

class MessageQueueType:
    QPID = 1
    RABBITMQ = 2


class AccessMode:
    READ  = 0x01
    WRITE = 0x02
    RW = READ|WRITE