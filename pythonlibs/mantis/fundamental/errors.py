#coding:utf-8

from basetype import ValueEntry


class ErrorCodeMixer:
    def code(self):
        pass

class ErrorDefs(ErrorCodeMixer):
    __BASE__ = 1000


class ErrorEntry(ValueEntry):
    def __init__(self,*args,**kwargs):
        ValueEntry.__init__(self, *args,**kwargs)

def hash_object(obj):
    attrs = [s for  s in dir(obj) if not s.startswith('__')  ]
    kvs={}
    for k in attrs:
        attr = getattr(obj, k)
        if not callable(attr):
            kvs[k] = attr
    return kvs
