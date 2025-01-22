from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite


def current_site_url(site):
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'https')
    port = getattr(settings, 'MY_SITE_PORT', '')
    url = f'{protocol}://{site.domain}'
    if port:
        url += f':{port}'
    return url


def current_site(request):
    """Context processor to add the "current site" to the current Context,
    also ads fully qualified URL (no trailing slash) for the current site.
    """
    version = settings.VERSION
    try:
        site = Site.objects.get_current()
    except Site.DoesNotExist:
        site = RequestSite(request)
    return {'site': site, 'base_url': current_site_url(site), 'version': version}
