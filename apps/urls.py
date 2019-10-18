from django.urls import include, path
from django.conf import settings
from django.contrib import admin

from views import home, docs, logmeout, sitemap
from feedback.views import feedback
from profile import profile

urlpatterns = [
    path('', home),
    path('feedback', feedback),
    path('vocabularies/', include('vocabulary.urls')),
    path('tag/', include('tag.urls')),

    path('accounts/', include('registration.backends.default.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('profile', profile, name='profile'),
    path('docs', docs, name='docs'),
    path('docs-nav-queries', docs),
    path('pay/', include('pay.urls')),
    path('logout/', logmeout, name='auth_logout'),
    path('sitemap.xml', sitemap, name='sitemap'),
]

admin.site.site_header = settings.SITE_NAME
admin.site.site_title = settings.SITE_NAME
