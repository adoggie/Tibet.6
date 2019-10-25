#coding: utf-8

import json
from mantis.fundamental.utils.useful import hash_object,object_assign

"""
{
    id,
    name,
    values:{
        ..
    }:
}

"""

JsonMessageSplitter = '\0'


class JsonMessage(object):
    NAME = ''
    def __init__(self,name):
        self.id_ = ''
        self.name_ = name
        self.values_ = {}
        self.extras_ = {}

    def assign(self,data):
        object_assign(self,data)

    def marshall(self,splitter=JsonMessageSplitter):
        data = dict(id=self.id_,name=self.name_,values=self.values(),extras=self.extras())
        return  json.dumps(data) + splitter

    def values(self):
        return hash_object(self,excludes=('id_','name_','values_','extras_','NAME'))

    def extras(self):
        return self.extras_

