from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.static import serve

urlpatterns = patterns('',
    url(r'^rhino/',include('django.rhino.urls')),
    # url(r'^webapi/common/',include('service.common.urls')),
	# url(r'^api/fileserver/',include('service.appserver.urls')),
	# url(r'^$','service.common.http.root'),	# root page
	# url(r'^admin/$','service.common.http.admin'),	# root page
	# url(r'^admin/.*\.html$','service.common.http.loadPage',{'prefix':'/admin/'}),
	# url(r'^pages/.*\.html$','service.common.http.loadPage',{'prefix':'/'}),
	# url(r'^.*\.html$','service.common.http.loadPage'),
	url(r'^static/(?P<path>.*)$',serve,{'document_root':settings.STATIC_ROOT+'static','show_indexes':True}),

)