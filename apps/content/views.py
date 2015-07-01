from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from vocabulary.models import Concept, Vocabulary
from content.models import Page
from content.forms import PageForm

@login_required
def site(request):
    try:
        vocab = Vocabulary.objects.filter(queries=True)[0]
        concepts = vocab.concept_set.filter(parent__isnull=True).order_by('order')
    except:
        vocab = False
        concepts = False
    return render(request, 'content/base.html', {'vocabulary': vocab, 'concepts': concepts})

def autocomplete(request):
    q = request.GET.get('q','').strip().lower()
    concepts = Concept.objects.filter(name__istartswith=q)
    return render(request, 'content/autocomplete.txt', {'concepts': concepts})

def search(request):
    return redirect('/content')

def page(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    change = reverse('admin:content_page_change', args=(page.id,))
    return render(request, 'content/page.html', {'page': page, 'change': change})

@login_required
def page_edit(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect(page.get_absolute_url())
    else:
        form = PageForm(instance=page)
    return render(request, 'content/page-form.html', {'page': page, 'form': form })
