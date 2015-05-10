from django.contrib.auth.views import logout
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from vocabulary.models import Vocabulary
from utils import render

def sitemap(request):
    base_href = 'http://'+Site.objects.get_current().domain+'/'
    vocabularies = Vocabulary.objects.all().order_by('-updated_at')
    rendered = render_to_string('sitemap.xml', {'vocabularies':vocabularies, 'base_href':base_href})
    return HttpResponse(rendered, content_type='application/xml')

def home(request):
    return render('home.html', {}, request)

def docs(request):
    return render('docs.html', {}, request)

def logmeout(request):
    messages.success(request, '<b>Logged out.</b> Thanks for spending some quality time with the Web site today.')
    return logout(request, '/')