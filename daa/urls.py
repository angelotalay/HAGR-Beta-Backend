from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    url(r'^$', 'daa.atlas.views.index', name='home'),
    url(r'^atlas/', include('daa.atlas.urls')),
    url(r'^tools/', include('daa.tools.urls')),
    url(r'^goterms/', include('daa.go_db.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^admin/', include(admin.site.urls)),
    url(r'^bibliography/', include('daa.django_libage.urls', namespace='libage')),
	url(r'^external/submissions/', include('daa.submissions.urls')),
)
