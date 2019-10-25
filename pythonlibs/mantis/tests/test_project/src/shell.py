#coding:utf-8



from mantis.fundamental.flask.database import db

from flask import Flask,request,g
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/scott/Desktop/yto/svn/camel_trans/trans_record.db'
db.set(SQLAlchemy(app))

from model.user import User


db.drop_all()
db.create_all()






