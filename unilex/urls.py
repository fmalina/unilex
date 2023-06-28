from django.urls import include, path, re_path
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import RedirectView

from unilex.views import home, pro, docs, logmeout, sitemap
from unilex.feedback.views import feedback
from unilex.profile import profile
from unilex.translit import translit_view

urlpatterns = [
    path('', home),
    path('feedback', feedback),
    path('tree/', include('unilex.vocabulary.urls')),
    path('tag/', include('unilex.tag.urls')),

    path('', include('allauth.urls')),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('profile', profile, name='profile'),
    path('docs', docs, name='docs'),
    path('docs-nav-queries', docs),
    path('pro', pro, name='pro'),
    path('pro/', include('pay.urls')),
    path('logout/', logmeout, name='auth_logout'),
    path('sitemap.xml', sitemap, name='sitemap'),

    path('med', RedirectView.as_view(url='/med/', permanent=True)),
    path('med/', include('medd.urls')),
    re_path(r'^(?P<s>.*)$', translit_view, name='translit'),
]

admin.site.site_header = settings.SITE_NAME
admin.site.site_title = settings.SITE_NAME

handler404 = "unilex.translit.handle404"
