from unilex.feedback.models import Feedback
from django.contrib.sites.models import Site
from django.http import Http404, HttpResponse
import datetime


def feedback(request):
    if not request.POST.get('feedback_message', '').strip():
        raise Http404
    site = Site.objects.get_current()
    url = request.META.get('HTTP_REFERER', '').replace('\n', '').strip()
    url = url.removeprefix(f'https://{site.domain}')
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '') or request.META.get('REMOTE_ADDR', '')

    if request.user.is_authenticated:
        user = request.user
        email = user.email
    else:
        user = None
        email = request.POST.get('feedback_email', '').strip()
    Feedback.objects.create(
        user=user,
        url=url,
        browser=request.META.get('HTTP_USER_AGENT', '').strip(),
        message=request.POST.get('feedback_message', '').strip(),
        ip=ip[:255],
        email=email,
        awesome=False,
        ignore=False,
        created_at=datetime.datetime.now(),
    )
    return HttpResponse('')
