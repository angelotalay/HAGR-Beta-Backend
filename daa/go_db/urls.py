from django.conf.urls import *

urlpatterns = patterns('daa.go_db.views',
    (r'^$', 'index'),
    (r'^go_to_changes/$', 'go_to_changes'),
)
