# coding:utf-8


"""
https://github.com/libwilliam/flask-compress
https://github.com/closeio/Flask-gzip

pip install :
  gevent
  Flask
  flask-compress
  flask-sqlalchemy
  flask-cors

"""

import time
import os
from threading import Thread

# from gevent import pywsgi
# from gevent import wsgi

import platform

# if platform.system() == 'Windows':
#     from wsgiref.simple_server import make_server
# else:
#     from gevent import pywsgi

from flask import Flask,request,g
from flask import Flask,Blueprint
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_compress import Compress
# from flask.ext.gzip import Gzip


from mantis.fundamental.utils.importutils import *
from mantis.fundamental.utils.useful import Instance
from mantis.fundamental.application import Application,instance
# from mantis.biz.application.srvmgr import ServiceManager

from mantis.fundamental.service import ServiceBase
from mantis.fundamental.logging.logger import Logger

db = Instance()


class FlaskService( ServiceBase):
    TYPE = 'FlaskService'

    def __init__(self, name):
        super(FlaskService,self).__init__(name)
        self.app = None

        self.api_list = {}  # 注册api
        self.db = None
        self.blueprints = {}
        self.logger = Logger(__name__)
        self.isclosed = False
        self.thread = None
        self.server = None

    def init(self, cfgs, **kwargs):
        #from mantis.fundamental.application.app import instance
        if kwargs.has_key('logger'):
            self.logger = kwargs.get('logger')

        self.cfgs = cfgs
        if kwargs.has_key('app'):
            self.app = kwargs.get('app')
        else:
            static_path = os.getcwd()+'/static'
            template_path = os.getcwd()+'/templates'
            self.app = Flask(__name__,static_folder=static_path,template_folder=template_path)  # flask会自动将当前代码目录设置为项目根目录 root_path 导致读取templtes , sta它ic 目录失败

        Compress(self.app)  # okay
        # gzip = Gzip(app) # error

        active = self.getConfig().get('cfgs',{})
        for k, v in active.items():
            self.app.config[k] = v

        self.initCors()
        self.initDatabase()

        self.setupRequestHooks()
        self.initBlueprint()

        self.setupTemplates()

    def setupTemplates(self):
        from werkzeug.routing import BaseConverter
        from flask import Flask, send_file
        class RegexConverter(BaseConverter):
            def __init__(self, map, *args):
                self.map = map
                self.regex = args[0]

        self.app.url_map.converters['regex'] = RegexConverter

        @self.app.route('/<regex(".*\.html$"):template_name>')
        def _template_render(template_name):
            name = os.path.join(self.app.template_folder, template_name)
            return send_file(name)


    def initDatabase(self):
        global db
        if db.get() is None:
            self.db = SQLAlchemy(self.app)
            db.set(self.db)

    def getDatabase(self):
        return self.db

    def initCors(self):
        """
            https://flask-cors.readthedocs.io/en/latest/
        :return:
        """
        if self.getConfig().get('cors_enable',True):
            CORS(self.app)

    def getFlaskApp(self):
        return self.app

    def setupRequestHooks(self):
        self.app.before_request(self.onRequestBefore)
        self.app.teardown_request(self.onRequestTeardown)
        # self.app.after_request(self._requestAfter)  # todo. 导致 send_file 失败
        # 当利用send_file发送二进制数据时，after_request对返回数据进行日志处理，导致数据返回失败

    def _traceRequestInfo(self,opts):
        import json
        trace_data = {'url':request.url}
        if opts.get('header'):
            trace_data['headers'] = request.headers
        if opts.get('body'):
            trace_data['body'] = request.data.replace('\n',' ')[:opts.get('max_size')]
        return json.dumps( trace_data)

    def _traceResponseInfo(self,opts,response):
        import json
        trace_data = {'url':request.url}
        if opts.get('header'):
            trace_data['headers'] = response.headers
        if opts.get('body'):
            trace_data['body'] = response.data.replace('\n',' ')[:opts.get('max_size')]
        return json.dumps( trace_data)

    def onRequestBefore(self):
        # pass
        import time
        g.start_time = time.time()

        #
        # trace = self.getConfig().get('http_trace',{}).get('request',{})
        # options = trace.get('options',{'header':False,'body':False,'max_size':1024})
        # urls = trace.get('urls',[])
        # #sort urls by 'match' with desceding.
        # urls = sorted(urls,cmp = lambda x,y: cmp(len(x.get('match')) , len(y.get('match')) ) )
        # urls.reverse()
        #
        # text = ''
        # for url in urls:
        #     m = url.get('match')
        #     if m:
        #         opts = options.copy()
        #         opts['header'] = url.get('header',options.get('header'))
        #         opts['body'] = url.get('body',options.get('body'))
        #         opts['max_size'] = url.get('max_size',options.get('max_size'))
        #         if request.url.find(m) !=-1:
        #             text = self._traceRequestInfo(opts)
        #             break
        # level = self.getConfig().get('http_trace',{}).get('level','DEBUG')
        # text = 'HttpRequest: '+text
        # self.getLogger().log(level,text)

    def onRequestTeardown(self,e):
        pass

    def _requestAfter(self,response):

        trace = self.getConfig().get('http_trace', {}).get('response', {})
        options = trace.get('options', {'header': False, 'body': False, 'max_size': 1024})
        urls = trace.get('urls', [])

        urls = sorted(urls, cmp=lambda x, y: cmp(len(x.get('match')), len(y.get('match'))))
        urls.reverse()

        text = ''
        for url in urls:
            m = url.get('match')
            if m:
                opts = options.copy()
                opts['header'] = url.get('header', options.get('header'))
                opts['body'] = url.get('body', options.get('body'))
                opts['max_size'] = url.get('max_size', options.get('max_size'))
                if request.url.find(m) != -1:
                    text = self._traceResponseInfo(opts,response)
                    break
        level = self.getConfig().get('http_trace', {}).get('level', 'DEBUG')

        remote_addr = ''
        if request.headers.getlist("X-Forwarded-For"):
            remote_addr = request.headers.getlist("X-Forwarded-For")[0]
        else:
            remote_addr = request.remote_addr

        elapsed = int((time.time() - g.start_time) * 1000)
        text = 'HTTP %s %s %s %sms  '%( remote_addr ,request.method,request.url,elapsed)
        self.getLogger().log(level, text)

        return response

    def initBlueprint(self):

        cfgs = self.getConfig().get('blueprints',[])
        for cfg in cfgs:
            # module = import_module( cfgs.get('module'))
            if not cfg.get('register',True):
                continue
            package_name = cfg.get('name','')
            package = cfg.get('package')
            package_url = cfg.get('url')
            modules = cfg.get('modules',[])
            for module in modules:
                module_name = module.get('name',)
                module_url = module.get("url",'')
                path = '%s.%s'%(package,module_name)
                load_module = import_module(path)

                app = Blueprint(module_name,path)
                self.blueprints[path] = app

                # api_module = {'name': u'%s.%s'%(package_name,module_name),'api_list':[]}
                module_name = u'%s.%s'%(package_name,module_name)
                self.api_list[module_name] = []

                routes = module.get('routes',[])
                for route in routes:
                    url = route.get('url','')
                    name = route.get('name','')
                    methods = filter(lambda x:len(x)>0,route.get('methods','').strip().upper().split(','))

                    if hasattr( load_module,name):
                        func = getattr( load_module,name)
                        path = package_url+module_url
                        path  = path.replace('//','/')
                        if methods:
                            app.route(url,methods=methods)(func)
                        else:
                            app.route(url)(func)
                        self.registerBlueprint(app,path)
                        # path = path + '/' + url
                        path = path + url  # todo. 2018.11.04 
                        path = path.replace('//','/')
                        self.logger.debug('registered blueprint route:'+path)

                        api = {'url': path,
                                'methods': ('GET',)}

                        if methods:
                            api['methods'] = methods
                        self.api_list[module_name].append(api)


    def registerAPIs(self,manager):
        manager.register_http_service(self.api_list)


    # def _initLogger(self):
    #     from camel.biz.logging.logger import FlaskHttpRequestLogger
    #     return FlaskHttpRequestLogger(self.appId)

    # def start(self,block = True):
    #     # Application.run(self)
    #     http = self.getConfig().get('http')
    #     if http:
    #         self.app.run(host=http.get('host','127.0.0.1'),
    #             port = http.get('port',5000),
    #             threaded = http.get('threaded',True),
    #             debug = http.get('debug',True),
    #             process = http.get('process',1))

    def select_address(self):
        """
        修正http侦听地址 ， 如果port未定义或者为0 ，则进行动态选定端口
        :return:
        """
        from mantis.fundamental.utils.network import select_address_port
        http = self.cfgs.get('http')

        if not http.get('port'): # port 未定义或者为0
            start = 18900
            end = 18950
            address = select_address_port(http.get('host'),start,end)
            self.cfgs.get('http')['port'] = address[1]

    def start(self, block=True):
        self.select_address()

        http = self.getConfig().get('http')
        host = http.get('host','127.0.0.1')
        port = http.get('port',5000)
        # app = self.app

        # if http.get('debug', False):
        #     app.run(host,port,debug=True)
        # else:
        #     self.server = wsgi.WSGIServer(( host, port), app)
        #
        #     self.server.start()
        #     Application.run(self)
        # self.server = pywsgi.WSGIServer((host,port),app)
        # self.server.start()



        self.initHttpServer()

        if block:
            self.logger.info('Service: %s started, Listen on %s:%s ...' % (self.name, host, port))
            self.server.serve_forever()
        else:
            self.thread = Thread(target=self.runThread)
            self.thread.setDaemon(True)
            self.thread.start()


    def initHttpServer(self):
        http = self.getConfig().get('http')
        host = http.get('host', '127.0.0.1')
        port = http.get('port', 5000)
        app = self.app
        from mantis.fundamental.application.use_gevent import USE_GEVENT

        print '--' * 20
        if USE_GEVENT:
            from gevent import pywsgi
            from socketio.server import SocketIOServer
            if http.get('websocket',False):
                self.server = SocketIOServer((host, port), app, resource="socket.io")
            else:
                self.server = pywsgi.WSGIServer((host, port), app)
                self.server.start()
        else:
            from wsgiref.simple_server import make_server
            self.server = make_server(host, port, app)

        self.logger.info('Service: %s started, Listen on %s:%s ...' % (self.name, host, port))

    def runThread(self):
        # print 'xxxx-Service: %s started, Listen on %s:%s ...' % (self.name, host, port)
        self.server.serve_forever()


    def stop(self):
        from mantis.fundamental.application.use_gevent import USE_GEVENT

        if self.server:
            if USE_GEVENT:
                self.server.stop()
            else:
                self.server.shutdown()

    def registerBlueprint(self,bp,url):
        self.app.register_blueprint( bp , url_prefix= url )



__all__=(db,FlaskService,)