#coding:utf-8



class ValueEntry:
    def __init__(self,value,comment=''):
        self.value = value
        self.comment = comment

    def __get__(self, instance, owner):
        return self.value

    def __str__(self):
        return str(self.value)

    @property
    def str(self):
        return str(self.value)

    @property
    def v(self):
        return self.value


CAMEL_HOME='/srv/camel'

