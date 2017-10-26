from django.conf.urls import url, include
from django.conf import settings
from django.views.static import serve
from django.contrib import admin
admin.autodiscover()

from views import home, docs, logmeout, sitemap
from feedback.views import feedback
from profile import profile

urlpatterns = [
    url(r'^$', home),
    url(r'^feedback$', feedback),
    url(r'^vocabularies/', include('vocabulary.urls')),
    url(r'^tag/', include('tag.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile$', profile, name='profile'),
    url(r'^docs$', docs, name='docs'),
    url(r'^docs-nav-queries$', docs),
    url(r'^pay/', include('pay.urls')),
    url(r'^logout/$', logmeout, name='auth_logout'),
    url(r'^sitemap.xml$', sitemap, name='sitemap'),
    # uncomment if you don't use a reverse proxy
    url(r'^(.*)', serve, {'document_root': settings.STATIC_ROOT}),
]
