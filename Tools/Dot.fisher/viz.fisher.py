#coding:utf-8

import graphviz

from graphviz import Digraph
from mantis.fundamental.utils.useful import hash_object
from mantis.sg.fisher.stbase.tradeobject import TradeObject

dot = Digraph(comment='mantis.sg.fisher')
s = Digraph('structs', node_attr={'shape': 'record'})


def hash_object(obj,excludes=()):
    attrs = [s for  s in dir(obj) if not s.startswith('__')  ]
    kvs={}
    mems =[]
    funs = []
    name = obj.__class__.__name__
    for k in attrs:
        if k in excludes:
            continue
        attr = getattr(obj, k)
        if callable(attr):
            funs.append(k)
        else:
            mems.append(k)
    mems.sort(cmp=lambda x,y: x>y)
    return name,mems,funs


obj = TradeObject(None,None)
name,mems,funs = hash_object(obj)
funs = map(lambda f:'*'+f+'()',funs)
s.node(name,'{%s|%s|%s}'%(name,'|'.join(mems),'|'.join(funs)) )
s.view()