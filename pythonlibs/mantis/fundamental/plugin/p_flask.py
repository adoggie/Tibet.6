#coding:utf-8


"""
https://github.com/libwilliam/flask-compress
https://github.com/closeio/Flask-gzip

"""
import time
from gevent import wsgi,spawn
from flask import Flask,request,g
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_compress import Compress
from flask.ext.gzip import Gzip


from mantis.fundamental.utils.importutils import *
# from mantis.fundamental.utils.useful import Instance
from mantis.fundamental.application import Application,instance
from mantis.fundamental.plugin.base import BasePlugin
from mantis.fundamental.flask.database import db
# db = Instance()

class FlaskServiceFacet( BasePlugin):
    def __init__(self,id):
        BasePlugin.__init__(self,id,'flask')

        self._flask_app = None
        self._db = None
        self._cfgs = {}
        self._api_list = {}  # 注册api

        # if kwargs.get('db_init',False):
        #     Application.__init__(self)
        #     self._initConfig()
        # else:
        #     CamelApplication.__init__(self,*args,**kwargs)
        # self._initFlaskApp()

    def init(self,cfgs):
        self._cfgs = cfgs
        if not self.flask_app:
            self._flask_app = Flask(__name__)  # flask会自动将当前代码目录设置为项目根目录 root_path 导致读取templtes , sta它ic 目录失败
        Compress(self.flask_app)  # okay
        for k, v in cfgs.get('cfgs',{}).items():
            self.flask_app.config[k] = v
        CORS(self.flask_app)
        """https://flask-cors.readthedocs.io/en/latest/"""
        if not self._db:
            self._db = SQLAlchemy(self.flask_app)
            db.set(self._db)

        self._initRequestHooks()
        self._initBlueprint()

    # def _initFlaskApp(self,app=None):
    #     # if not app:
    #     #     app = Flask(__name__)  # flask会自动将当前代码目录设置为项目根目录 root_path 导致读取templtes , sta它ic 目录失败
    #     # self.app = app
    #     # Compress(app)  # okay
    #     # # gzip = Gzip(app) # error
    #     #
    #     # self._initFlaskConfig()
    #     # self._initFlaskCors()
    #
    #     global db
    #     if db.get() is None:
    #         self.db = SQLAlchemy(self.app)
    #         db.handle = self.db
    #
    #     self._initRequestHooks()
    #     self._initBlueprint()

    @property
    def database(self):
        return self._db

    @database.setter
    def database(self,value):
        self._db = value

    @property
    def flask_app(self):
        return self._flask_app

    def _initRequestHooks(self):
        pass
        # self.flask_app.before_request(self._requestBefore)
        # self.flask_app.teardown_request(self._requestTeardown)

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

    def _requestBefore(self):
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

    def _requestTeardown(self,e):
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
        # self.getLogger().log(level, text)

        return response

    def _initBlueprint(self):
        from flask import Blueprint

        self.blueprints = {}

        cfgs = self._cfgs.get('routes',[])
        for cfg in cfgs:
            # module = import_module( cfgs.get('module'))
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
                self._api_list[module_name] = []

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
                        path = path + '/' + url
                        path = path.replace('//','/')
                        instance.getLogger().debug('registered blueprint route:'+path)

                        api = {'url': path,
                                'methods': ('GET',)}

                        if methods:
                            api['methods'] = methods
                        self._api_list[module_name].append(api)

            # ServiceManager.instance().register_http_service(self.api_list)

    @property
    def routeConfigs(self):
        return self.cfgs.get('routes')

    # def _initLogger(self):
    #     from camel.biz.logging.logger import FlaskHttpRequestLogger
    #     return FlaskHttpRequestLogger(self.appId)

    def open(self,block=False):
        if block:
            self.run()
        else:
            spawn(self.run)

    def registerBlueprint(self,bp,url):
        self.flask_app.register_blueprint( bp , url_prefix= url )

    def close(self):
        pass

    def run(self):
        mode = self.cfgs.get('run_mode', 'normal')
        if mode == 'wsgi':
            self.run_wsgi()
        self.run_normal()

    def run_normal(self):
        http = self.cfgs.get('http')
        if http:
            self.flask_app.run(host=http.get('host', '127.0.0.1'), port=http.get('port', 5000),
                threaded=http.get('threaded', True), debug=http.get('debug', True),
                # process=http.get('process', 1)
                )

    def run_wsgi(self):
        http = self.cfgs.get('http')
        host = http.get('host', '127.0.0.1')
        port = http.get('port', 5000)
        print 'Server Started, Listen on %s:%s ...' % ( host, port)
        server = wsgi.WSGIServer((host, port), self.flask_app)
        server.serve_forever()

MainClass = FlaskServiceFacet

# def setup(cls = ServiceFlaskApplication):
#     return cls.instance()
#
#
# __all__=(db,FlaskApplication,ServiceFlaskApplication,instance,setup)
__all__ = (MainClass,)