#coding:utf-8


import getopt
import os
import sys
import os.path

# from  use_gevent import Event
from threading import Event

from mantis.fundamental.utils.useful import Instance,Singleton
from mantis.fundamental.basetype import CAMEL_HOME
from mantis.fundamental.logging.logger import Logger
from mantis.fundamental.parser.yamlparser import YamlConfigParser
from mantis.fundamental.logging.filter import LogHandlerFilter
from mantis.fundamental.utils.timeutils import timestamp_to_str,timestamp_current

instance = Instance()

class Application(Singleton,object):
    inst = None
    def __init__(self,name=''):
        self.name = name
        self.conf = {}
        self.caches = None
        self.logger = Logger(__name__)
        self.db = None
        self.config_file ='settings.yaml'
        self.log_filters = {}
        self.plugins ={}
        self.pluginsIndexed =[]
        self.wait_ev = Event()
        self.props ={}
        self.actived = False
        self.inited = False
        self.aborted = False

        global instance
        instance.set(self)

    def setProps(self,**kwargs):
        self.props.update(kwargs)

    def getProp(self,name,default_=None):
        return self.props.get(name,default_)

    @property
    def datasourceManager(self):
        from mantis.fundamental.datasource import DatasourceManager
        return DatasourceManager()

    @property
    def serviceManager(self):
        from mantis.fundamental.service import ServiceManager
        return ServiceManager()

    @property
    def messageBrokerManager(self):
        from mantis.fundamental.messagebroker import MessageBrokerManager
        return MessageBrokerManager()

    def getService(self,name):
        from mantis.fundamental.service import ServiceManager
        return ServiceManager().get(name)

    def registerPlugin(self,plugin):
        """注册插件"""
        self.plugins[plugin.id] = plugin
        self.pluginsIndexed.append(plugin)

    def setupPlugins(self):
        from mantis.fundamental.plugin import init_plugins
        init_plugins()
        for p in self.pluginsIndexed:
            p.open()

    def closePlugins(self):
        for p in self.pluginsIndexed:
            p.close()

    def getPlugin(self,name,type=None):
        plugin = self.plugins.get(name)
        if plugin:
            if type and type != plugin.type:
                return None
        return plugin

    def getPlugins(self,type):
        result =[]
        for p in self.pluginsIndexed:
            if p.type ==  type:
                result.append(p)
        return result


    @property
    def appName(self):
        app_name = self.getConfig().get('app_name','')
        return app_name

    @property
    def appId(self):
        prj_ver = self.getConfig().get('project_version', '')
        name = "%s.%s-%s" % (self.projectName, self.name, os.getpid())
        return name

    def setName(self,name):
        self.name = name
        return self

    def getName(self):
        return self.name

    @property
    def projectName(self):
        prj_name = self.getConfig().get('project_name','')
        return prj_name

    def getDefaultConfigFile(self):
        if self.config_file and self.config_file[0] == '/':
            return self.config_file  # absoluted path
        return os.path.join(self.getConfigPath(),self.config_file )

    def getHomePath(self):
        # path = os.getenv('CAMEL_HOME')
        # if path:
        #     return os.path.join(path,'products',self.name)
        path = os.getenv('APP_PATH')
        if path:
            return path+'/..'
        path = os.getcwd() + '/..'
        return path

        # path = os.path.join(self.getCamelHomePath(), 'products', self.name)
        # if not os.path.exists(path):
        #     return os.path.dirname(os.path.abspath(__file__))
        # return os.path.join(self.getCamelHomePath(), 'products', self.name)

    def getConfigPath(self):
        return os.path.join( self.getHomePath(),'etc')

    def getDataPath(self):
        return os.path.join(self.getHomePath(), 'data')

    def getTempPath(self):
        return os.path.join(self.getHomePath(), 'temp')

    def getLogPath(self):
        return os.path.join(self.getHomePath(), 'logs')

    def getRunPath(self):
        return os.path.join(self.getHomePath(), 'run')

    def getLogger(self):
        return self.logger

    def getCamelHomePath(self):
        path = os.getenv('CAMEL_HOME')
        if path:
            return path

        return os.path.join(self.getHomePath(),'../')
        # path = os.getcwd()+'/..'
        # return path
        # return os.path.dirname(os.path.abspath(__file__))+'/..'
        # return CAMEL_HOME


    def getConfig(self):
        return self.conf

    def usage(self):
        pass

    def initOptions(self):
        """从环境变量 APP_NAME 拾取appname
           从命令行 --name 参数拾取appname
        :return:
        """
        if self.name:
            return
        self.name = os.getenv('APP_NAME')
        options, args = getopt.getopt(sys.argv[1:], 'hc:n:', ['help', 'name=','config=']) # : 带参数
        for name, value in options:
            if name in ['-h', "--help"]:
                self.usage()
                sys.exit()
            if name in ('-n', '--name'):
                self.name = value
            if name in ('-c','--config'):
                self.config_file = name

        if not self.name:
            self.name = ''

    def initDirectories(self):
        from distutils.dir_util import mkpath
        mkpath(self.getConfigPath())
        mkpath(self.getDataPath())
        mkpath(self.getLogPath())
        mkpath(self.getRunPath())
        mkpath(self.getTempPath())


    def initServices(self):
        self.serviceManager.init(self.getConfig().get('services'))

    def initDatasources(self):
        self.datasourceManager.init(self.getConfig().get('datasources'))

    def initMessageBrokers(self):
        self.messageBrokerManager.init(self.getConfig().get('message_brokers'))

    def init(self):

        self.initOptions()
        self.initDirectories()
        self.initConfig()
        self.initLogs()
        self.initPlugins()
        self.initSignal()
        self.initDatasources()
        self.initServices()
        self.initMessageBrokers()
        self.initEnd()
        self.inited = True

        return self

    def initPlugins(self):
        self.setupPlugins()

    def initEnd(self):
        """ create pid file
        """

        pid = os.getpid()
        # filename = os.path.join(self.getRunPath(),'server_{}.pid'.format(timestamp_to_str( timestamp_current())))
        filename = os.path.join(self.getRunPath(),'server.pid')
        fp = open(filename,'w')
        fp.write('%s'%pid)
        fp.close()


    def initConfig(self):
        yaml = self.getDefaultConfigFile()
        self.conf = YamlConfigParser(yaml).props
        self._checkConfig()
        if not self.name:
            self.name = self.conf.get('app_name','')

    def _checkConfig(self):
        """检查配置项是否okay"""
        pass

    def initLogger(self):
        return Logger(self.appName)

    def initLogs(self):
        import logging,string

        # ver = self.conf.get('project_version')
        # project = self.conf.get('project_name')
        # app_id = self.appName
        self.logger = self.initLogger()

        log = self.conf.get('logging')
        level = log.get('level','INFO')
        self.logger.setLevel(level) # 不能设置全局，否则会默认输出到console

        # extra = {'project_name':project,'project_version':ver,'app_id':app_id,'tags':''}
        formatter = logging.Formatter(log.get('format'))
        self.logger.setFormat(formatter)
        # self.logger.setMessageFormat(log.get('message_format'))
        # self.initLogHandlerFilters(log.get('filters',{}))

        handlers = log.get('handlers',[])
        for cfg in handlers:
            handler = self.initLogHandler(cfg)
            if handler:
                # handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                # ss = cfg.get('filter', '').strip()
                # if ss:
                #     ss = map( string.strip ,ss.split(',') )
                #     for s in ss:
                #         flt = self.log_filters.get(s)
                #         if flt:
                #             handler.addFilter(flt)
                #         else:
                #             print 'error: filter<%s> not found!'%s


    def initLogHandlerFilters(self,cfgs):
        filters = {}
        for name,cfg in cfgs.items():
            flt = LogHandlerFilter(name,cfg)
            filters[name] = flt
        self.log_filters = filters

    def initLogHandler(self,cfg):
        """日志handler初始化
        目前仅支持: file(RotatingFileHandler) , console(StreamHandler)

        :param cfg:
        :return:
        """
        from mantis.fundamental.logging.handler import  LogFileHandler,LogConsoleHandler

        handler = None
        if cfg.get('type','').lower() == LogFileHandler.TYPE and cfg.get('enable', False) == True:
            logfile = os.path.join(self.getLogPath(), cfg.get('filename'))
            handler = LogFileHandler(logfile, encoding=cfg.get('encoding'), maxBytes=cfg.get('max_bytes'),
                backupCount=cfg.get('backup_count'))

        if cfg.get('type').lower() == LogConsoleHandler.TYPE and cfg.get('enable', False) == True:
            handler = LogConsoleHandler()

        return handler

    def run(self):
        if self.aborted:
            return
        self.actived = True
        self.datasourceManager.open()
        self.serviceManager.start()
        self.messageBrokerManager.start()

        forks = self.getConfig().get('forks',0)
        if forks:
            pids = []
            for nr in range(forks):
                pid = os.fork()
                if pid == 0: # child process
                    break
                else:
                    pids.append( pid )
            if pids: #  father process, wait until children all terminated
                 for pid in pids:
                    os.waitpid(pid)
        print 'Service [%s] Started..' % self.name
        self.serve_forever()
        self.serviceManager.join()
        print 'Service [%s] Stopped..' % self.name

    def serve_forever(self):
        while not self.wait_ev.is_set() and self.actived:
            self.wait_ev.wait(1)

        print 'serve_forever run end..'

    def abort(self):
        self.aborted = True

    def stop(self):
        # self.inited = False
        self.actived = False
        # print 'To Stop Server..'
        self.messageBrokerManager.stop()
        self.serviceManager.stop()
        self.datasourceManager.close()
        self.wait_ev.set()

    def initSignal(self):
        """多线程时, signal 被发送到创建的子线程中，主线程无法捕获"""
        import signal
        signal.signal(signal.SIGINT, self._sigHandler)

    def _sigHandler(self,signum, frame):
        print 'signal ctrl-c'
        self.stop()


def setup(cls):
    return cls.instance()

__all__=(instance,Application,setup)



