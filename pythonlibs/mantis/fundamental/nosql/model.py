#coding:utf-8

# 基於 mongodb 的 ORM

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.useful import hash_object,object_assign
from bson import ObjectId

database = None

def get_database():
    return database

"""
_id - mongodb object id 
id() - 获得 _id 的字符类型

"""
class Model(object):
    __database__ = None
    def __init__(self):
        self._id = None
        self.__collection__ = self.__class__.__name__

    class QuerySet(object):
        def __init__(self,collection):
            self.coll = collection
            self.rs = None

        def exec_(self,**kwargs):
            self.rs = self.coll.find(kwargs)
            return self

        def sort(self,order_flags):
            pass


    @property
    def id_(self):
        return str(self._id)

    @classmethod
    def get_database(cls):
        return cls.__database__

    @classmethod
    def find(cls,**kwargs):
        clsname = cls.__name__
        coll = cls.get_database()[clsname]
        rs = coll.find(kwargs)
        result =[]
        for r in list(rs):
            obj = cls()
            object_assign(obj,r , add_new=True)
            result.append(obj)
        return result

    @classmethod
    def find2(cls, **kwargs):
        clsname = cls.__name__
        coll = cls.get_database()[clsname]
        # not implemented

    def dict(self):
        data = hash_object(self)
        if data.has_key('_id'):
            del data['_id']
        return data

    # @staticmethod
    # def get(self,**kwargs):
    #     pass

    @classmethod
    def collection(cls):
        coll = cls.get_database()[cls.__name__]
        return coll

    @classmethod
    def get(cls,**kwargs):
        obj = cls()
        coll =  cls.get_database()[cls.__name__]
        data = coll.find_one(kwargs)
        if data:
            object_assign(obj,data, add_new=True)
            return obj
        return None

    @classmethod
    def get_or_new(cls, **kwargs):
        obj = cls.get(**kwargs)
        if not obj:
            obj = cls()
            object_assign(obj,kwargs)
        return obj

    def assign(self,data , add_new = True):
        object_assign(self,data,add_new= add_new)
        return self

    def delete(self):
        """删除当前对象"""
        coll = self.get_database()[self.__collection__]
        coll.delete_one({'_id':self._id})

    def update(self,**kwargs):
        """执行部分更新"""
        coll = self.get_database()[self.__collection__]
        coll.update_one({'_id':self._id},update={'$set':kwargs},upsert = True)
        return self

    def save(self):
        coll = self.get_database()[self.__collection__]
        data = hash_object(self, excludes=['_id','id_'])
        if self._id:
            self.update(**data)
        else:
            self._id = coll.insert_one(data).inserted_id
        return self

    @classmethod
    def spawn(cls,data):
        """根据mongo查询的数据集合返回类实例"""

        # 单个对象
        if isinstance(data,dict):
            obj = cls()
            object_assign(obj,data)
            return obj
        # 集合
        rs = []
        for r in data:
            obj = cls()
            object_assign(obj, data)
            rs.append(obj)
        return rs

    @classmethod
    def create(cls,**kwargs):
        obj = cls()
        object_assign(obj,kwargs)
        return obj

    def __getattr__(self, name):
        return self.__dict__.get(name,None)

    def get_value(self,name,default=None):
        value = self.__dict__.get(name,None)
        if not value:
            value = default
        return value

def set_database(space,database):
    for k,v in space.items():
        if isinstance(v,type):
            if issubclass(v,Model) and v != Model :
                setattr(v,'__database__',database)