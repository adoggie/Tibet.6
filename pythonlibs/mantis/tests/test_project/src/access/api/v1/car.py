#coding:utf-8

from flask import Blueprint,request,g
from mantis.fundamental.flask.database import db
from mantis.fundamental.application.app import instance

app = Blueprint('zoo',__name__)

# @app.route('/car')
def car():
    instance.getLogger().debug('abccc')
    instance.getLogger().addTag('TRANS:A001')
    # print request.values
    do_request()
    return 'i am car!'

def do_request():
    instance.getLogger().debug('xxx')


# @app.route('/cat')
def cat():
    import time
    time.sleep(.2)
    instance.getLogger().debug('miao~')
    return 'i am cat!'


# @app.route('/online')
def lines():

    # line = Online()
    # line.get_time = '2017-1-1'
    # line.mobile = '13916624477'
    #
    # db.session.add(line)
    # db.session.commit()

    # return 'one online record  be created! <%s>'%line.id
    pass