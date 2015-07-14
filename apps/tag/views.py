from django.forms.formsets import formset_factory
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from vocabulary.forms import *
from vocabulary.models import Concept, Vocabulary
from tag.forms import TagForm, RecordForm, PageForm
from tag.models import Page
from tag.get import Get, GetError
from tag.post import post_tags
import settings

def nothing(request):
    ''' Nothing to tag '''
    return HttpResponse('We can\'t tag this page.')

def about(request):
    ''' Page about tagging, install Chrome extension '''
    return render(request, 'tag/about.html', {})
    
@csrf_exempt
def tag(request, node_id):
    ''' For a given piece of content identified by its node_id
        GET: makes a SRU request & displays returned tags in a compelling interface
        POST: makes a SWORD post to save user entered tags for a given node_id '''
    if request.method == 'POST':
        record_form = RecordForm(request.POST)
        if record_form.is_valid():
            auth_token = record_form.cleaned_data['auth_token']
            record = {
                'title':       record_form.cleaned_data['title'],
                'description': record_form.cleaned_data['description'],
                'notes':       record_form.cleaned_data['notes'],
                'name':        record_form.cleaned_data['name'],
                'node_id':     record_form.cleaned_data['node_id'],
            }
            TagFormSet = formset_factory(form=TagForm)
            formset = TagFormSet(request.POST)
            tags = []
            for form in formset.forms:
                raw_tag = form['to_concept'].data
                try:
                    tag = Concept.objects.get(pk=raw_tag)
                    tags.append(tag)
                except:
                    pass
            return HttpResponse(post_sword(record, tags, auth_token))
        else:
            return HttpResponse('Record form was invalid.')
    else: # GET
        query = '(ns.nid="%s")' % node_id
        try:
            record = Get(request, query).parse()[0]
        except GetError:
            messages.error(request, 'Sorry, we can\'t pull tags from the CMS right now.<br>' \
                'Connection has timed out. Reload to try again')
            import traceback
            return HttpResponse(traceback.format_exc(), content_type='text/plain')
            
        raw_tags = record['tags']
        tags = []
        tag_forms = []
        for raw_tag in raw_tags:
            try:
                vocab = Vocabulary.objects.get(node_id=raw_tag[0])
                try:
                    tag = Concept.objects.get(vocabulary=vocab, node_id=raw_tag[1])
                    tag_form = {'to_concept': tag.id,}
                    tags.append(tag)
                    tag_forms.append(tag_form)
                except:
                    messages.info(request, '''Concept "%s" from vocab "%s"
                        is not loaded in the repository.''' % (raw_tag[1], vocab))
            except:
                messages.info(request, '<b>%s</b> is not loaded in the repository.' % raw_tag[0])
        if not tags:
            tags = ['addfirst']
        TagFormSet = formset_factory(form=TagForm, extra=len(tags), can_delete=True)
        form = RecordForm(record)
        formset = TagFormSet(initial=tag_forms)
        forms_and_tags = zip(formset.forms, tags)
        return render(request, 'tag/tag.html', {
            'form': form,
            'formset': formset,
            'forms_and_set': forms_and_tags
            })

def query(request):
    ''' Return list of results for a given CQL query '''
    query = request.POST['query']
    records = Get(request, query).parse()
    return render(request, 'tag/query-results.html', {
        'tag_server_url': settings.TAG_SERVER_URL,
        'links': records
        })

@login_required
def site(request):
    vocab = Vocabulary.objects.first()
    concepts = vocab.concept_set.filter(parent__isnull=True).order_by('order')
    return render(request, 'tag/base.html', {'vocabulary': vocab, 'concepts': concepts})

def autocomplete(request):
    q = request.GET.get('q','').strip().lower()
    concepts = Concept.objects.filter(name__istartswith=q)
    return render(request, 'tag/autocomplete.txt', {'concepts': concepts})

def search(request):
    return redirect('/tag/site')

def page(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    change = reverse('admin:tag_page_change', args=(page.id,))
    return render(request, 'tag/page.html', {'page': page, 'change': change})

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
    return render(request, 'tag/page-form.html', {'page': page, 'form': form })
