import json

from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from tag.client import Client
from tag.forms import TagForm, RecordForm
from tag.models import Tag, Record
from vocabulary.models import Concept, Vocabulary


class TaggingView(View):
    """For a given piece of content identified by its URL
    GET: request tags & displays returned tags in a compelling interface
    POST: post tags to save user entered tags for a given url.

    Communicate with local database or proxy remote source using Client.
    """
    template_name = 'tag/record-form.html'
    remote = False

    @method_decorator(csrf_exempt)
    def post(self, request, url):
        record, created = Record.objects.get_or_create(url=url)
        form = RecordForm(request.POST, instance=record)
        tag_formset = formset_factory(form=TagForm)
        formset = tag_formset(request.POST)

        if not form.is_valid():
            print(form.errors)
        else:
            d = form.cleaned_data
            tags = []
            for tag_form in formset.forms:
                raw_tag = tag_form['to_concept'].data
                if raw_tag:
                    tag = Concept.objects.get(pk=raw_tag)
                    tags.append(tag)
            if self.remote:
                print('remote')
                response = HttpResponse(Client.post_tags(d, tags, d['auth_token']))
            else:
                record.title = d['title']
                record.save()
                for tag in tags:
                    print(tag)
                    _tag, _created = Tag.objects.get_or_create(record=record, concept=tag)
                response = redirect(record.get_absolute_url())
            return response

    def get(self, request, url):
        tag_concepts = []
        tag_forms = []

        if self.remote:  # remote source of tagging data
            query = url
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
            record, created = Record.objects.get_or_create(url=url)
            concepts = [tag.concept for tag in record.tag_set.all()]

        for concept in concepts:
            tag_form = {'to_concept': concept.id, }
            tag_concepts.append(concept)
            tag_forms.append(tag_form)
            # messages.info(request, '''Concept "%s" from vocab "%s"
            #     is not loaded in the repository.''' % (tag.concept, vocab))
            # messages.info(request, '<b>%s</b> is not loaded in the repository.' % tag.concept)
        if not tag_concepts:
            tag_concepts = ['addfirst']
        tag_formset = formset_factory(form=TagForm, extra=len(tag_concepts), can_delete=True)
        form = RecordForm(instance=record)
        formset = tag_formset(initial=tag_forms)
        forms_and_tags = zip(formset.forms, tag_concepts)
        response = render(request, self.template_name, {
            'record': record,
            'form': form,
            'formset': formset,
            'forms_and_set': forms_and_tags
        })
        # CORS header
        response['Access-Control-Allow-Origin'] = '*'
        return response


def about(request):
    """Introduction to tagging, install Chrome extension link
    """
    return render(request, 'tag/about.html', {})


def query(request):
    """Return list of results for a given tag query
    """
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
    """JSON rendered single record with its tags
    """
    record = get_object_or_404(Record, pk=record_id)
    tags = record.tag_set.all()
    return render(request, 'tag/record.js',
                  {'record': record, 'tags': tags},
                  content_type="application/json")
