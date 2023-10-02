from django.conf import settings
from django.conf.urls import include, patterns, url

urlpatterns = patterns('daa.atlas.views',
    (r'^$', 'index'),
    (r'^about/$', 'about'),
    (r'^help/$', 'help'),
    (r'^downloads/$', 'downloads'),
    (r'^contact/$', 'contact'),
    (r'^results/$', 'results'),
    (r'^anatomical/$', 'anatomical'),
    (r'^change/(?P<identifier>DAA\d+)/$', 'change'),
    (r'^gene/(?P<entrez_id>\d+)/$', 'gene'),
    (r'^tissue/(?P<evid>\d+)/$', 'tissue'),
    (r'^reference/(?P<id>\d+)/$', 'reference'),
    (r'^saved/(?P<method>\w+)/$', 'saved'),
    (r'^json/$', 'return_as_json'),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )