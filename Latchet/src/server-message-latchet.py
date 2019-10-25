#coding:utf-8


from mantis.fundamental.application.use_gevent import use_gevent
use_gevent()
from socketio import server, namespace, socketio_manage

from mantis.fundamental.application.app import Application,instance,setup

class LatchetApplication(Application):
    def __init__(self):
        Application.__init__(self)

    # def serve_forever(self):
    #     server.SocketIOServer(
    #         ('localhost', 9090), self, policy_server=False).serve_forever()
    #
    #     print 'serve_forever run end..'

setup(LatchetApplication).init().run()


