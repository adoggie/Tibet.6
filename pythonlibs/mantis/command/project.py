#coding:utf-8

import os,os.path
import sys
import shutil

def createApp(name,path):
    """创建应用"""
    webapp = os.path.join( os.path.dirname(os.path.abspath(__file__))+'/..','templates','webapp')

    dest = os.path.join(path,name)
    if not os.path.exists(path):
        os.makedirs(path)
    shutil.copytree(webapp,dest)
    shutil.move(dest+'/src/webapp',dest+'/src/'+name)
    print 'create app finished.'

if __name__ == '__main__':
    createApp('abc','ddd')