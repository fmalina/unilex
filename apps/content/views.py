from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required
from vocabulary.models import Concept, Vocabulary
from content.models import Page
from content.forms import PageForm
from utils import render

@login_required
def site(request):
    try:
        vocab = Vocabulary.objects.filter(queries=True)[0]
        concepts = vocab.concept_set.filter(parent__isnull=True).order_by('order')
    except:
        vocab = False
        concepts = False
    return render('content/base.html', {
        'vocabulary': vocab,
        'concepts': concepts
        }, request)

def autocomplete(request):
    q = request.GET.get('q','').strip().lower()
    concepts = Concept.objects.filter(name__istartswith=q)
    return render('content/autocomplete.txt', {'concepts': concepts}, request)

def search(request):
    return HttpResponseRedirect('/content')

def page(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    change = urlresolvers.reverse('admin:content_page_change', args=(page.id,))
    return render('content/page.html', {
        'page': page,
        'change': change
        }, request)

@login_required
def page_edit(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(page.get_absolute_url())
    else:
        form = PageForm(instance=page)
    return render('content/page-form.html', {
        'page': page,
        'form': form
        }, request)
