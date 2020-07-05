import os
from datetime import datetime
from json import dumps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from paging import simple_paging
from utils import ajax_login_required
from vocabulary.export_csv import export_csv
from vocabulary.export_json import vocab_to_dict
from vocabulary.export_skos import export_skos
from vocabulary.forms import UploadFileForm, VocabularyForm, \
    ConceptForm, NewChildConceptForm, RelatedForm, ParentForm
from vocabulary.models import Authority, Vocabulary, Concept
from sentry_sdk import capture_exception


NOT_ALLOWED = 'You are not allowed to edit this vocabulary.'


def listings(request, *args, **kwargs):
    ls = Vocabulary.objects.with_counts().exclude(private=True).order_by(
        'language', 'user_id', 'title')
    return render(request, 'vocabulary/listings.html', {'ls': ls})


def filter_private(qs, user):
    """Filters out private terms"""
    if user.is_authenticated:
        qs = qs.filter(
            Q(vocabulary__private=False) |
            Q(vocabulary__user=user) |
            Q(vocabulary__authority__users=user)
        )
    else:
        qs = qs.filter(vocabulary__private=False)
    return qs.distinct().order_by('-count')


def autocomplete(request):
    q = request.GET.get('q','').strip()
    concepts = Concept.objects.filter(
        Q(name__icontains=q) |
        Q(node_id__istartswith=q)
    )
    concepts = filter_private(concepts, request.user)
    response = render(request, 'vocabulary/autocomplete.txt', {'concepts': concepts})
    response['Access-Control-Allow-Origin'] = '*'
    return response


def search(request):
    q = request.GET.get('q', '').strip()
    ls = Concept.objects.filter(
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(node_id__istartswith=q)
    )
    ls = filter_private(ls, request.user)
    if not q:
        ls = []
    ls, count, paging = simple_paging(request, ls, 10)
    return render(request, 'vocabulary/search.html', {
        'ls': ls, 'count': count, 'paging': paging,
        'q': q,
        'title': f'{q} - Search results'
    })


def load_vocab(request, format='xls', authority_code=''):
    from vocabulary.load_xls import load_xls, XLSLoadException
    from vocabulary.load_skos import SKOSLoader

    form = UploadFileForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fn = file.name.split('.')[0].split('/')[-1]
            f = file.read()
            # save the raw file into an S3 bucket
            if form.cleaned_data.get('permit', False):
                upload_path = os.path.join(settings.PROJECT_ROOT, 'uploads', file.name)
                fw = open(upload_path, 'wb')
                fw.write(f)
                fw.close()

            goto = '/vocabularies/'
            # parse and load into the DB
            if format == 'xls':
                try:
                    goto = load_xls(request.user, f, fn)
                except Exception as e:
                    messages.error(request, f"That didn't work: {e}")
                    capture_exception(e)
                    return redirect('load', 'xls')
            if format == 'skos':
                try:
                    loader = SKOSLoader(request.user)
                    goto, msgs = loader.load_skos_vocab(f)
                    for level, msg in msgs:
                        messages.add_message(request, level, msg)
                    loader.save_relationships()
                    messages.success(request, loader)
                except Exception as e:
                    messages.error(request, f"That didn't work: {e}")
                    capture_exception(e)
                    return redirect('load', 'skos')

            if goto and isinstance(goto, Vocabulary) and authority_code:
                vocab = goto
                vocab.authority = get_object_or_404(Authority, code=authority_code)
                vocab.save()

            return redirect(goto)

    return render(request, 'vocabulary/upload.html', {'form': form, 'format': format})


@login_required
def vocabulary_add(request, authority_code=''):
    vocab = Vocabulary(title='New vocabulary')
    vocab.user = request.user
    if authority_code:
        vocab.authority = get_object_or_404(Authority, code=authority_code)
    vocab.save()
    return redirect(vocab.get_absolute_url())


def authority(request, authority_code, json=False):
    """Authority and its vocabularies."""
    a = get_object_or_404(Authority, code=authority_code)
    ls = Vocabulary.objects.with_counts().filter(authority=a)
    # TODO: ACL API
    # private_access = request.user in a.users.all()
    # if not private_access:
    #     ls = ls.filter(private=False)
    context = {
        'ls': ls,
        'authority': a,
        'authority_code': a.code,
        'private_access': True  # private_access
    }
    if json:
        ls = [{
            'name': v.title,
            'node_id': v.node_id,
            'url': v.get_absolute_url() + 'json'
        } for v in ls]
        return HttpResponse(dumps(ls), content_type='application/json')
    return render(request, 'vocabulary/authority.html', context)


def pro_message(action="accessing", why_upgrade="pro features"):
    return f"""You are {action} a private vocabulary,
        but your professional subscription is not active,
        <a href="/pro/subscribe">please subscribe</a>
        to enable {why_upgrade or action}."""


def detail(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if vocab.private and not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)
    if vocab.private and not vocab.user.subscription.is_active:
        messages.info(request, pro_message())
    count = Concept.objects.filter(vocabulary=vocab).count()
    concepts = vocab.concept_set.filter(parent__isnull=True)
    return render(request, 'vocabulary/detail.html', {
        'vocabulary': vocab,
        'count': count,
        'concepts': concepts
    })


def json(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    # TODO: ACL API
    # if vocab.private and not vocab.is_allowed_for(request.user):
    #    raise Http404(NOT_ALLOWED)
    count = Concept.objects.filter(vocabulary=vocab).count()
    max_depth = 0
    if not count < 2000:
        max_depth = 3
    jsondata = dumps(vocab_to_dict(vocab, max_depth), indent=4)
    return HttpResponse(jsondata, content_type='application/json')


def export(request, vocab, data, extension, mime):
    if vocab.private and not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)
    if vocab.private and not vocab.user.subscription.is_active:
        messages.info(request, messages.info(request, pro_message('exporting', 'export'))
        return redirect(vocab.get_absolute_url())
    timestamp = datetime.today().strftime('%Y-%m-%d')
    response = HttpResponse(data, content_type=mime)
    response['Content-Disposition'] = 'attachment; filename="%s-%s.%s"' % (
        vocab.node_id, timestamp, extension)
    return response


def skos(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    return export(request, vocab, export_skos(vocab), 'xml', 'application/rdf+xml')


def csv(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    s = export_csv(vocab)
    return export(request, vocab, s, 'csv', 'text/comma-separated-values')


def ul(request, vocab_node_id, style='meeting'):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if vocab.private and not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)
    concepts = vocab.concept_set.filter(parent__isnull=True).order_by('order')
    return render(request, f'vocabulary/view-{style}.html', {
        'vocabulary': vocab,
        'concepts': concepts
    })


@ajax_login_required
@csrf_exempt
def ordering(request, vocab_node_id):
    """Child concepts are ordered by ID if no order is specified.
    
    This view allows to set new ordering using concept.order.
    
    Request POST will look like:
        {'order_concept_478[]': ['2', '1', '3']} or
        {'order_vocab_15[]': ['1', '2', '5'...
    Where 478 is parent concept PK and 2, 1, 3 is new ordering
    of the children to rewrite their starting sequence 1, 2, 3.
    Ordering sequence numbers are not the same thing as concept.order
    
    Ordering the 1st level differs as instead of parent concept PK we get a vocab PK.
    """
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)

    x = 'Order concepts'
    if request.method == 'POST':
        orderword_modelword_pk, seq = list(dict(request.POST).items())[0]
        orderword, modelword, pk = orderword_modelword_pk.split('_')
        pk=int(pk.replace('[]',''))
        if modelword == 'concept':
            model = Concept
        else:
            model = Vocabulary
        parent = get_object_or_404(model, pk=pk)
        children = dict(enumerate(parent.get_children(), start=1)) # old order
        sequence = list(enumerate([int(x) for x in seq], start=1)) # new order mapping
        # print(children) >>> {1: <Concept: CSS>, 2: <Concept: JS>, 3: <Concept: HTML>}
        # print(sequence) >>> [(1, 3), (2, 1), (3, 2)] # desired order HTML, CSS, JS
        for new_concept_order, forloop_counter in sequence:
            concept = children[forloop_counter]
            concept.order = new_concept_order
            concept.save()
        x = 'Updated order'
    return HttpResponse(x)


@csrf_exempt
def vocabulary_edit(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = VocabularyForm(request.POST, instance=vocab)
            if form.is_valid():
                form.save()
            return redirect(vocab.get_absolute_url())
        else:
            return redirect('/')
    else:
        form = VocabularyForm(instance=vocab)
    return render(request, 'vocabulary/vocabulary-edit.html', {
        'vocabulary': vocab,
        'children': vocab.get_children(),
        'form': form
    })


@ajax_login_required
def concept_new(request, vocab_node_id, node_id=0):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)

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
            return redirect(parent.get_absolute_url())
    else:
        form = NewChildConceptForm(instance=c)
    return render(request, 'vocabulary/new-concept.html', {
        'concept': c,
        'parent': parent,
        'form': form
    })


@csrf_exempt
def concept_edit(request, vocab_node_id, node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)

    c = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
    children = c.get_children()
    related = c.related.all()
    parent = c.parent.all()
    if not related:
        related = ['addfirst']
    if not parent:
        parent = ['addfirst']
    RelatedFormSet = inlineformset_factory(
        Concept,
        Concept.related.through,
        fk_name="subject",
        form=RelatedForm,
        extra=1,
        can_delete=True
    )
    ParentFormSet = inlineformset_factory(
        Concept,
        Concept.parent.through,
        fk_name="from_concept",
        form=ParentForm,
        extra=1,
        can_delete=True
    )
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ConceptForm(request.POST, instance=c)
            formset = RelatedFormSet(request.POST, instance=c, prefix='rf')
            parent_formset = ParentFormSet(request.POST, instance=c, prefix='pf')
            if form.is_valid():
                form.save()
            if formset.is_valid():
                formset.save()
            if parent_formset.is_valid():
                parent_formset.save()
            return redirect(c.get_absolute_url())
        else:
            return redirect('/')
    else:
        form = ConceptForm(instance=c)
        formset = RelatedFormSet(instance=c, prefix='rf')
        parent_formset = ParentFormSet(instance=c, prefix='pf')
    return render(request, 'vocabulary/concept-edit.html', {
        'children': children,
        'concept': c,
        'form': form,
        'formset': formset,
        'parent_formset': parent_formset,
        'forms_and_set': zip(formset.forms, related),
        'parent_forms_and_set': zip(parent_formset.forms, parent)
    })


@csrf_exempt
@ajax_login_required
def concept_adopt(request):
    if request.method != 'POST':
        raise Http404('post only')

    def get_objs(node_ids):
        if not node_ids:
            raise Http404('no data')
        vocab_node_id, node_id = node_ids.split(':')
        vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
        if not vocab.is_allowed_for(request.user):
            raise Http404(NOT_ALLOWED)

        concept = None
        if node_id != 'direct_to_parent_vocab':
            concept = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
        return vocab, concept

    child_vocab, child = get_objs(request.POST.get('child'))
    parent_vocab, parent_concept = get_objs(request.POST.get('parent'))

    if child == parent_concept:
        return HttpResponse('protected from pasting to itself')

    child.parent.remove(child.mother())
    if parent_concept:
        child.parent.add(parent_concept)
    child.save()

    if child_vocab != parent_vocab:
        child.vocabulary = parent_vocab
        child.save()
        for d in child.get_descendants():
            d.vocabulary = parent_vocab
            try:
                d.save()
            except:
                pass

    return HttpResponse('ok')


@ajax_login_required
def concept_delete(request, vocab_node_id, node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)

    c = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
    if request.method == 'POST':
        if c.mother():
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
    return render(request, 'vocabulary/concept-delete.html', {'concept': c})


@ajax_login_required
def vocabulary_delete(request, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if not vocab.is_allowed_for(request.user):
        raise Http404(NOT_ALLOWED)

    allowed = False
    if request.user == vocab.user or request.user.is_staff:
        allowed = True
        if request.method == 'POST':
            if 'understand' in request.POST:
                vocab.delete()
                messages.success(request, f'"{vocab.title}" is now deleted.')
                return redirect('/vocabularies/')
            messages.info(request, 'Not deleted. You need to tick the box to confirm.')
            return redirect(vocab.get_absolute_url())
    return render(request, 'vocabulary/vocabulary-delete.html', {
        'vocabulary': vocab,
        'allowed': allowed
    })
