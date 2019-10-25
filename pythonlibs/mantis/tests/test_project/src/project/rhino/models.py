#coding:utf-8

from django.db import models
from datetime import datetime


class User(models.Model):
    name = models.CharField(max_length=128,db_index=True)
    value = models.CharField(max_length=512,null=True)
    comment = models.CharField(max_length=256,null=True)
    delta = models.TextField(null=True)

class App(models.Model):
    pass