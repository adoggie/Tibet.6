# coding:utf-8

__doc__ = u'celery 服务端功能类'

from celery import Celery,current_app
from camel.fundamental.utils.importutils import import_module
from camel.fundamental.utils.useful import get_config_item
from camel.fundamental.application.app import instance


# class CeleryQueue:
#     def __init__(self,service,cfg):
#         self.cfg = cfg
#         self.service = service

class CeleryTask:
    def __init__(self,service,cfg):
        self.service = service
        self.cfg = cfg
        self.name = cfg.get('name')
        self.path = cfg.get('path')
        self.routing_key = cfg.get('routing_key')
        self.queue = cfg.get('queue')

    @property
    def task_id(self):
        return '%s.%s'%(self.path,self.name)

    def open(self):

        module = import_module( self.path )
        func = None
        if  hasattr(module,self.name):
            func = getattr(module,self.name)
        if func is None:
            print 'cannot find task:',self.name, ' in module:',self.path
            return False
        print 'registered celery task: ',self.name

        self.service.app.task(func)
        return True


class CeleryService:
    def __init__(self,cfg):
        self.cfg = cfg
        self.exchange = cfg.get('exchange',{})
        self.name = cfg.get('name')
        self.route = cfg.get('route',{})
        self.queues = {}
        for _ in cfg.get('queues',[]):
            self.queues[_.get('name')] =_
        self.tasks = {}

        for task_cfg in cfg.get('tasks',[]):
            task = CeleryTask(self, task_cfg )
            self.tasks[task.task_id] = task

        self.app = None

        self.init()


    def init(self):
        from kombu import Queue

        self.app = Celery(self.name, broker=self.route.get('broker'), backend=self.route.get('backend'))

        self.app.conf['CELERY_DEFAULT_EXCHANGE'] = self.exchange.get('name', 'tasks')
        self.app.conf['CELERY_DEFAULT_EXCHANGE_TYPE'] = self.exchange.get('type')
        self.app.conf['CELERY_DEFAULT_QUEUE'] = self.cfg.get('default_queue', 'default')
        self.app.conf['CELERY_QUEUES'] = []
        # self.app.conf['CELERYD_POOL'] = "prefork"
        for qcfg in self.queues.values():
            q = Queue(qcfg.get('name'), routing_key=qcfg.get('routing_key'))
            self.app.conf['CELERY_QUEUES'].append(q)
        self.app.conf['CELERY_ROUTES'] = {}
        for task in self.tasks.values():
            key = '%s.%s.%s' % (self.name, self.exchange.get('name'), task.name)
            value = {'queue': task.queue, 'routing_key': task.routing_key}
            self.app.conf['CELERY_ROUTES'][key] = value

    def open(self):
        import gevent
        for task in self.tasks.values():
            task.open()
        gevent.spawn(self._asServer())
        return True

    def _asServer(self):
        from celery.bin import worker
        wkr = worker.worker(app = self.app)
        options = {'loglevel': 'INFO', 'traceback': True, }
        wkr.run(**options)

    def _log(self,category,name,args):
        logger = instance.getLogger()
        root_cfg = instance.getConfig()
        level = root_cfg.get('level','INFO')

        text = '[Celery] categary:%s name:%s args:%s '%(category,name,args)


        text = text.replace('\n','')

        logger.log(level,text)

    def send_task(self,name,*args,**kwargs):
        task = self.tasks.get(name)
        if task:
            queue = task.queue
            kwargs['queue'] = queue
            self.app.send_task(name,*args,**kwargs)
            args = kwargs.get('args',())
            text = ''
            if args:
                text = reduce(lambda x, y: x + ' ,' + y, map(str, args))
                max_size = get_config_item(instance.getConfig(),'celery_trace.client_max_size',0)
                text = text[:max_size]
            self._log('send_task',name,text)

# http://docs.jinkan.org/docs/celery/userguide/routing.html

"""
CELERY_ROUTES = {
    'tasks.add': {'exchange': 'C.dq', 'routing_key': 'w1@example.com'}
}

CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'
BROKER_TRANSPORT = 'redis'

# http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html
# http: // docs.jinkan.org / docs / celery /

"""