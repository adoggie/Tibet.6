#coding:utf-8

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.importutils import import_class

"""
默认插件的classpath在 mantis.fundamental.plugin.xxxx
用户也可以指定其他路径的插件

myapp.plugins.myplugin.py

class MyPlugin(BasePlugin):
    pass

settings.yaml
    plugin_1:
        class: 'myapp.plugins.myplugin.MyPlugin'

"""

def init_plugins():
    cfgs = instance.getConfig().get('plugins',[])
    for name in cfgs:
        cfg =instance.getConfig().get(name)
        if not cfg:
            instance.getLogger().warning("plugin:{} not found!".format(name))
            continue
        plugin_type = cfg.get('type','undefined')
        classpath = 'mantis.fundamental.plugin.p_{}.MainClass'.format(plugin_type)
        classpath = cfg.get('class',classpath)
        CLS = import_class(classpath)
        plugin = CLS(name)
        plugin.init(cfg)
        instance.registerPlugin(plugin)

