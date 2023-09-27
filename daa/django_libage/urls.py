from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.search_references),
    url(r'^entry/(?P<identifier>\w+)/$', views.reference, name='entry'),
    url(r'^search/$', views.search_references, name='search'),
)
