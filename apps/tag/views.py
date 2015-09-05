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
from tag.forms import TagForm, RecordForm
from tag.models import Tag, Record
from tag.client import Client
import settings
import json

def about(request):
    """Introducton to tagging, install Chrome extension link"""
    return render(request, 'tag/about.html', {})


def record_edit(request, record_id):
    """ Local editing mockup."""
    record = get_object_or_404(Record, pk=record_id)
    if request.method == 'POST':
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect(record.get_absolute_url())
    else:
        form = RecordForm(instance=record)
    return render(request, 'tag/record-form.html', {'record': record, 'form': form })


@csrf_exempt
def tag(request, node_id, remote=False):
    """For a given piece of content identified by its node_id
    GET: request tags & displays returned tags in a compelling interface
    POST: post tags to save user entered tags for a given node_id.
    
    Communicate with local database or proxy remote source using Client.
    """
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if record_form.is_valid():
            d = form.cleaned_data
            auth_token = d['auth_token']
            record = {
                'title'  : d['title'],
                'desc'   : d['desc'],
                'node_id': d['node_id'],
            }
            TagFormSet = formset_factory(form=TagForm)
            formset = TagFormSet(request.POST)
            tags = []
            for tag_form in formset.forms:
                raw_tag = tag_form['to_concept'].data
                tag = Concept.objects.get(pk=raw_tag)
                tags.append(tag)
            response = HttpResponse(Client.post_tags(record, tags, auth_token))
        else:
            response = HttpResponse('Record form was invalid.')
    else: # GET
        tag_concepts = []
        tag_forms = []
        
        if remote:
            # remote source of tagging data
            query = node_id
            try:
                data = Client(request, query).get_tags()
                json_record = json.loads(data)
            except Exception as e:
                msg = "Sorry, can't pull tags from the remote source right now.\nError was:\n\n"
                import traceback
                return HttpResponse(msg + traceback.format_exc(), content_type='text/plain')
            
            record = Record.objects.get(id=json_record['id'])
            concepts = []
            for t in json_record['tags']:
                t = t.split()
                vocab = Vocabulary.objects.get(node_id=t[0])
                concept = Concept.objects.get(vocabulary=vocab, node_id=t[1])
                concepts.append(concept)
        else:
            # local tag repository
            record = Record.objects.get(id=node_id)
            concepts = [tag.concept for tag in record.tag_set.all()]
        
        for concept in concepts:
            tag_form = {'to_concept': concept.id,}
            tag_concepts.append(concept)
            tag_forms.append(tag_form)
            # messages.info(request, '''Concept "%s" from vocab "%s"
            #     is not loaded in the repository.''' % (tag.concept, vocab))
            # messages.info(request, '<b>%s</b> is not loaded in the repository.' % tag.concept)
        if not tag_concepts:
            tag_concepts = ['addfirst']
        TagFormSet = formset_factory(form=TagForm, extra=len(tag_concepts), can_delete=True)
        form = RecordForm(instance=record)
        formset = TagFormSet(initial=tag_forms)
        forms_and_tags = zip(formset.forms, tag_concepts)
        response = render(request, 'tag/record-form.html', {
            'form': form,
            'formset': formset,
            'forms_and_set': forms_and_tags
        })
    # CORS headers
    response['Access-Control-Allow-Origin'] = '*'
    return response

def query(request):
    """Return list of results for a given tag query"""
    q = request.POST['query']
    return render(request, 'tag/query-results.html', {
        'records': Client(request, q).get_tags()
        })

def records(request):
    return render(request, 'tag/records.html', {
        'title': 'Recently tagged resources',
        'records': Record.objects.prefetch_related(
            'tag_set__concept',
            'tag_set__concept__vocabulary'
        )
    })

def record_json(request, record_id):
    """ JSON rendered single record with its tags """
    record = get_object_or_404(Record, pk=record_id)
    tags = record.tag_set.all()
    return render(request, 'tag/record.js',
        {'record': record, 'tags': tags},
        content_type="application/json")