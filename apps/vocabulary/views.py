from json import dumps
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from vocabulary.models import *
from vocabulary.forms import *
from vocabulary.export_skos import export_skos
from vocabulary.export_csv import export_csv
from vocabulary.export_json import vocab_to_dict
from utils import render, getCamelCase, ajax_login_required
from paging import simple_paging
from datetime import datetime

def listings(request, *args, **kwargs):
    listings = Vocabulary.objects.with_counts().exclude(private=True).order_by('title')
    return render('vocabulary/listings.html', {'listings': listings}, request)

def autocomplete(request):
    q = request.GET.get('q','').strip()
    concepts = Concept.objects.filter(
        Q(name__search=q) |
        Q(node_id__istartswith=q)
    )
    if not concepts:
        concepts = Concept.objects.filter(
            Q(name__icontains=q) |
            Q(node_id__istartswith=q)
        )
    concepts = concepts.order_by('-count')
    return render('vocabulary/autocomplete.txt', {'concepts': concepts}, request)

def search(request):
    q = request.GET.get('q','')
    ls = Concept.objects.filter(
        Q(name__search=q) |
        Q(description__search=q) |
        Q(node_id__istartswith=q)
    ).order_by('-count')
    ls, count, paging = simple_paging(request, ls, 10)
    return render('vocabulary/search.html', {
        'ls': ls,
        'q': q,
        'title': '%s - Search results' % q
        }, request)

def detail(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    count = Concept.objects.filter(vocabulary=vocab).count()
    concepts = vocab.concept_set.filter(parent__isnull=True)
    return render('vocabulary/detail.html', {
        'vocabulary': vocab,
        'count': count,
        'concepts': concepts}, request)

@login_required
def load_vocab(request, format='xls'):
    from vocabulary.load_xls import load_xls
    from vocabulary.load_skos import SKOSLoader
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if format=='xls':
                goto = load_xls(request, request.FILES['file'])
            if format=='skos':
                file = request.FILES['file'].read()
                loader = SKOSLoader(request)
                goto = loader.load_skos_vocab(file)
                
                loader.save_relationships()
                messages.success(request, loader)
            return redirect(goto)
    else:
        form = UploadFileForm()
    return render('vocabulary/upload.html', {'form':form, 'format': format}, request)

@login_required
def vocabulary_add(request):
    vocab = Vocabulary(title='New vocabulary')
    vocab.save()
    return redirect(vocab.get_absolute_url())

def json(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    jsondata = dumps(vocab_to_dict(vocab), indent=4)
    return HttpResponse(jsondata, content_type='application/json')

def export(request, vocab, data, extension, mime):
    timestamp = datetime.today().strftime('%Y-%m-%d')
    response = HttpResponse(data, content_type=mime)
    response['Content-Disposition'] = 'attachment; filename="%s-%s.%s"' % (getCamelCase(vocab.title), timestamp, extension)
    return response

def skos(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    return export(request, vocab, export_skos(vocab), 'xml', 'application/rdf+xml')

def csv(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    s = export_csv(vocab)
    return export(request, vocab, s, 'csv', 'text/comma-separated-values')

def glossary(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    concepts = vocab.concept_set.order_by('name')
    s = render_to_string('vocabulary/glossary.csv', {'concepts': concepts})
    return export(request, vocab, s, 'csv', 'text/comma-separated-values')

def ul(request, vocab_node_id, style='meeting'):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    concepts = vocab.concept_set.filter(parent__isnull=True).order_by('order')
    return render('vocabulary/view-%s.html' % style, {
        'vocabulary': vocab,
        'concepts': concepts
        }, request)

@login_required
def order(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    concepts = Concept.objects.filter(vocabulary=vocab)
    x = 'Order concepts'
    if request.method == 'POST':
        for c in concepts:
            raise # TODO
            c.order = int(request.POST['order']) 
            c.save()
        x = 'Updated order'
    return HttpResponse(x)

@csrf_exempt
def vocabulary_edit(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if request.method == 'POST':
        if request.user.is_authenticated():
            form = VocabularyForm(request.POST, instance=vocab)
            if form.is_valid():
                form.save()
            return redirect(vocab.get_absolute_url())
        else:
            return redirect('/')
    else:
        form = VocabularyForm(instance=vocab)
    return render('vocabulary/vocabulary-edit.html', {
        'vocabulary': vocab,
        'children': vocab.get_children(),
        'form': form
        }, request)

@ajax_login_required
def concept_new(request, vocab_node_id, node_id=0):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    c = Concept(vocabulary=vocab)
    if vocab_node_id:
        parent = vocab
        add_parent = False
    if node_id:
        parent = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
        add_parent = True
    if request.method == 'POST':
        form = NewChildConceptForm(request.POST, instance=c)
        if form.is_valid():
            c = form.save()
            if add_parent:
                c.parent.add(parent)
            c.save()
            if(c.mother()):
                gobackto = c.mother().get_absolute_url()
            else:
                gobackto = c.vocabulary.get_absolute_url()
            return redirect(gobackto)
    else:
        form = NewChildConceptForm(instance=c)
    return render('vocabulary/new-concept.html', {
        'concept': c,
        'parent': parent,
        'form': form
        }, request)

@csrf_exempt
def concept_edit(request, vocab_node_id, node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    c = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
    children = c.get_children()
    synonyms = c.synonym_set.all()    
    related = c.related.all()
    parent  = c.parent.all()
    if not related:
        related = ['addfirst']
    if not parent:
        parent = ['addfirst']
    RelatedFormSet = inlineformset_factory(
        Concept,
        Concept.related.through,
        fk_name="from_concept",
        form=RelatedForm,
        extra=len(related),
        can_delete=True
    )
    ParentFormSet = inlineformset_factory(
        Concept,
        Concept.parent.through,
        fk_name="from_concept",
        form=ParentForm,
        extra=len(parent),
        can_delete=True
    )
    if request.method == 'POST':
        if request.user.is_authenticated():
            form = ConceptForm(request.POST, instance=c)
            formset = RelatedFormSet(request.POST, instance=c, prefix='rf')
            parent_formset = ParentFormSet(request.POST, instance=c, prefix='pf')
            if form.is_valid() and formset.is_valid() and parent_formset.is_valid():
                form.save()
                formset.save()
                parent_formset.save()
            return redirect(c.get_absolute_url())
        else:
            return redirect('/')
    else:
        form = ConceptForm(instance=c)
        formset = RelatedFormSet(instance=c, prefix='rf')
        parent_formset = ParentFormSet(instance=c, prefix='pf')
    return render('vocabulary/concept-edit.html', {
        'children': children,
        'synonyms': synonyms,
        'concept': c,
        'form': form,
        'formset': formset,
        'parent_formset': parent_formset,
        'forms_and_set': zip(formset.forms, related),
        'parent_forms_and_set': zip(parent_formset.forms, parent)
        }, request)

@csrf_exempt
@ajax_login_required
def concept_adopt(request, vocab_node_id, node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    child = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
    mother = False
    if request.POST['mother'] != 'orphanate':
        mother = Concept.objects.get(node_id=request.POST['mother'])
    if request.method == 'POST':
        if child != mother: # protect from pasting to itself
            child.parent.remove(child.mother())
            if mother:
                child.parent.add(mother)
            child.save()
    return HttpResponse('ok')

@ajax_login_required
def concept_delete(request, vocab_node_id, node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    c = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
    if request.method == 'POST':
        if(c.mother()):
            gobackto = c.mother().get_absolute_url()
        else:
            gobackto = c.vocabulary.get_absolute_url()
        if 'recursive' in request.POST:
            for child in c.get_descendants():
                child.delete()
            c.delete()
        elif 'delete' in request.POST:
            for ch in c.get_children():
                ch.parent.remove(c)
                if c.mother():
                    ch.parent.add(c.mother())
            c.delete()
        return redirect(gobackto)
    return render('vocabulary/concept-delete.html', {'concept': c}, request)

@ajax_login_required
def vocabulary_delete(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if request.method == 'POST':
        if 'understand' in request.POST:
            vocab.delete()
            messages.success(request, '"%s" is now deleted.' % vocab.title)
            return redirect('/vocabularies/')
        else:
            messages.info(request, 'Not deleted. You need to tick the box to confirm.')
            return redirect(vocab.get_absolute_url())
    return render('vocabulary/vocabulary-delete.html', {'vocabulary': vocab}, request)