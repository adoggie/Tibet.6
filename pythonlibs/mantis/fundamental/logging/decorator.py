#coding:utf-8


def log_func(instance):
    """ 函数输出调用日志

        from camel.biz.application import instance

        @log_fun(instance)
        def init_database():
            ...

    """
    def _log_func(fx):
        def _wrapped(*args,**kwargs):
            instance.getLogger().debug('>>',fx.func_name,'()')
            return fx(*args,**kwargs)
        return _wrapped
    return _log_func

def auto_trace():
    pass
