from django.conf.urls import *

urlpatterns = patterns('daa.submissions.views',
    url(r'^$', 'index'),
)
