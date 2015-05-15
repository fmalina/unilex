from django.conf.urls import url, patterns, include
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'views.home'),
    (r'^feedback$', 'feedback.views.feedback'),
    (r'^vocabularies/', include('vocabulary.urls')),
    (r'^tag/', include('tag.urls')),
    (r'^content/', include('content.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^profile$', 'profile.profile', name='profile'),
    url(r'^docs$', 'views.docs', name='docs'),
    url(r'^logout/$', 'views.logmeout', name='auth_logout'),
    url(r'^sitemap.xml$', 'views.sitemap', name='sitemap'),
    # uncomment if you don't use a reverse proxy
    (r'^(.*)', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
