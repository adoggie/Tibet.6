#coding:utf-8

import unittest


class TestApp(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_service(self):
        from camel.biz.application.camelsrv import CamelApplication

        app = CamelApplication.instance()

        # app.getLogger().addTag('CS')
        # app.getLogger().debug('first line', tags='HOP,TRANS:A00912')
        # app.getLogger().error('http request timeout', tags='HOP,TRANS:A00912')
        # app.getLogger().removeTag('CS')
        # app.getLogger().setTags('HOPE,ENT')
        #
        # app.getLogger().debug('xxxx')
        # app.getLogger().setTransportTag('AK100001')  # 设置承运商
        # app.getLogger().debug('request in ')

    def test_flaskservice(self):
        from camel.biz.application.flasksrv import FlaskApplication
        app = FlaskApplication.instance()

        app.getLogger().addTag('CS')
        app.getLogger().debug('first line', tags='HOP,TRANS:A00912')
        app.getLogger().error('http request timeout', tags='HOP,TRANS:A00912')
        app.getLogger().removeTag('CS')
        app.getLogger().setTags('HOPE,ENT')

        app.getLogger().debug('xxxx')
        app.getLogger().setTransportTag('AK100001')  # 设置承运商
        app.getLogger().debug('request in ')

