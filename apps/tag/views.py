from django.forms.formsets import formset_factory
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from vocabulary.forms import *
from vocabulary.models import Concept, Vocabulary
from tag.forms import *
from tag.sru import Sru, SruError
from tag.sword import post_sword
from utils import render
import settings

def nothing(request):
    ''' Nothing to tag '''
    return HttpResponse('We can\'t tag this page.')

def about(request):
    ''' Page about tagging, install Chrome extension '''
    return render('tag/about.html', {}, request)
    
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
            record = Sru(request, query).parse()[0]
        except SruError:
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
        return render('tag/tag.html', {
            'form': form,
            'formset': formset,
            'forms_and_set': forms_and_tags
            }, request)

def query(request):
    ''' Return list of results for a given CQL query '''
    query = request.POST['query']
    records = Sru(request, query).parse()
    return render('tag/query-results.html', {
        'sru_server_url': settings.SRU_SERVER_URL,
        'links': records
        }, request)