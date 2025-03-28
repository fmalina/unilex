import os
from datetime import datetime
import hashlib
from json import dumps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import get_valid_filename

from unilex.paging import simple_paging
from unilex.utils import ajax_login_required
from unilex.vocabulary.export_csv import export_csv
from unilex.vocabulary.export_json import vocab_to_dict
from unilex.vocabulary.export_skos import export_skos
from unilex.vocabulary.forms import (
    UploadFileForm,
    VocabularyForm,
    User,
    AuthorityForm,
    ConceptForm,
    NewChildConceptForm,
    BaseRelatedFormSet,
    RelatedForm,
    PredicatesForm,
)
from unilex.vocabulary.models import Authority, Vocabulary, Concept
from sentry_sdk import capture_exception

NOT_ALLOWED = 'You are not allowed to view or edit this taxonomy'


def listings(request, *args, **kwargs):
    qs = Vocabulary.objects.with_counts()
    ls = qs.exclude(private=True).exclude(concept_count__lte=10).order_by('language', 'title')
    own = []
    if request.user.is_authenticated:
        own = qs.filter(user=request.user)
    return render(request, 'vocabulary/listings.html', {'ls': ls, 'own': own})


def filter_private(qs, user):
    """Filters out private terms"""
    if user.is_authenticated:
        qs = qs.filter(
            Q(vocabulary__private=False)
            | Q(vocabulary__user=user)
            | Q(vocabulary__authority__users=user)
        )
    else:
        qs = qs.filter(vocabulary__private=False)
    return qs.distinct().order_by('-count')


def autocomplete(request):
    q = request.GET.get('q', '').strip()
    concepts = Concept.objects.none()
    if q:
        concepts = Concept.objects.filter(Q(name__icontains=q) | Q(node_id__istartswith=q))
        concepts = filter_private(concepts, request.user)
    response = render(request, 'vocabulary/autocomplete.txt', {'concepts': concepts})
    response['Access-Control-Allow-Origin'] = '*'
    return response


def search(request):
    q = request.GET.get('q', '').strip()
    ls = Concept.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q) | Q(node_id__istartswith=q)
    )
    ls = filter_private(ls, request.user)
    if not q:
        ls = []
    ls, count, paging = simple_paging(request, ls, 10)
    return render(
        request,
        'vocabulary/search.html',
        {'ls': ls, 'count': count, 'paging': paging, 'q': q, 'title': f'{q} - Search results'},
    )


def generate(request):
    from unilex.vocabulary.ola import taxonomy_prompt, submit_prompt
    from unilex.vocabulary.load_md import load_md

    if request.method == 'POST' and request.user.is_authenticated:
        topic = request.POST.get('topic')
        try:
            text = submit_prompt(taxonomy_prompt(topic))
            v = load_md(request.user, text.encode('utf8'), topic)
            v.source = 'https://chat.openai.com'
            v.save()
            return redirect(v.get_absolute_url())
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'vocabulary/generate.html', {})


def load_vocab(request, format='xls', authority_code=''):
    from unilex.vocabulary.load_skos import SKOSLoader
    from unilex.vocabulary.load_xls import load_xls
    from unilex.vocabulary.load_md import load_md

    form = UploadFileForm()
    uploads_folder = os.path.join(settings.BASE_DIR, 'uploads')
    if request.method == 'POST' and request.user.is_authenticated:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get('file')
            content = form.cleaned_data.get('content')
            if file:
                fn = file.name.split('.')[0].split('/')[-1]
                # sanitise filename preventing directory traversal
                upload_fn = get_valid_filename(os.path.basename(file.name))
                content = file.read()
            else:
                fn = 'pasted'
                sha = hashlib.sha256(content.encode()).hexdigest()[:8]
                ext = 'csv' if format == 'xls' else format
                upload_fn = f'{fn}-{sha}.{ext}'
                content = content.encode()
            # save the raw file on disk
            if form.cleaned_data.get('permit', False):
                upload_path = os.path.join(uploads_folder, upload_fn)
                fw = open(upload_path, 'wb')
                fw.write(content)
                fw.close()

            # parse and load into the DB
            if format == 'md':
                try:
                    vocab = load_md(request.user, content, fn)
                except Exception as e:
                    messages.error(request, f"That didn't work: {e}")
                    capture_exception(e)
                    return redirect('load', 'md')
            if format == 'xls':
                try:
                    vocab = load_xls(request.user, content, fn)
                except Exception as e:
                    messages.error(request, f"That didn't work: {e}")
                    capture_exception(e)
                    return redirect('load', 'xls')
            if format == 'skos':
                try:
                    loader = SKOSLoader(request.user)
                    vocab, msgs = loader.load_skos_vocab(content)
                    for level, msg in msgs:
                        messages.add_message(request, level, msg)
                    if vocab:
                        loader.save_relationships()
                        messages.success(request, loader)
                    else:
                        return redirect('load', 'skos')
                except Exception as e:
                    messages.error(request, f"That didn't work: {e}")
                    capture_exception(e)
                    return redirect('load', 'skos')

            if vocab and authority_code:
                vocab.authority = get_object_or_404(Authority, code=authority_code)
                vocab.save()
            if vocab:
                return redirect(vocab.get_absolute_url())

    return render(request, 'vocabulary/upload.html', {'form': form, 'format': format})


@login_required
def vocabulary_add(request, authority_code=''):
    vocab = Vocabulary(title='New vocabulary')
    vocab.user = request.user
    if authority_code:
        vocab.authority = get_object_or_404(Authority, code=authority_code)
    vocab.save()
    return redirect(vocab.get_absolute_url())


def is_permitted(user, ath):
    return user in ath.users.all() or user.is_staff


def authority(request, authority_code, json=False):
    """Authority and its vocabularies."""
    ath = get_object_or_404(Authority, code=authority_code)
    ls = Vocabulary.objects.with_counts().filter(authority=ath)
    permitted = is_permitted(request.user, ath)
    form = AuthorityForm(request.POST or None, instance=ath)
    if form.is_valid() and permitted:
        form.save()
        return redirect('authority', authority_code=ath.code)
    context = dict(ls=ls, authority=ath, permitted=permitted, form=form)
    if json:
        ls = [dict(name=v.title, node_id=v.node_id, url=f'{v.get_absolute_url()}.json') for v in ls]
        return HttpResponse(dumps(ls), content_type='application/json')
    return render(request, 'vocabulary/authority.html', context)


def remove_user(request, authority_code, user_id):
    ath = get_object_or_404(Authority, code=authority_code)
    user = get_object_or_404(User, id=user_id)
    if is_permitted(request.user, ath) and user in ath.users.all():
        ath.users.remove(user)
    return redirect('authority', authority_code=ath.code)


def has_pro(user):
    try:
        return user.subscription.is_active
    except user._meta.model.subscription.RelatedObjectDoesNotExist:
        return False


def get_vocab(user, vocab_node_id):
    vocab = get_object_or_404(Vocabulary, node_id=vocab_node_id)
    if vocab.private and not vocab.is_allowed_for(user):
        raise Http404(NOT_ALLOWED)
    return vocab


def detail(request, vocab_node_id, style=None):
    vocab = get_vocab(request.user, vocab_node_id)
    if vocab.private and not has_pro(vocab.user):
        return redirect('subscribe')
    if style or request.path_info.endswith('/'):
        return redirect(vocab.get_absolute_url(), permanent=True)
    count = Concept.objects.filter(vocabulary=vocab).count()
    d = vocab_to_dict(vocab, 0)
    json_data = dumps(d, indent=4).encode()
    context = {
        'vocabulary': vocab,
        'concept_dict': d,
        'json_data': json_data.decode(),
        'count': count,
    }
    return render(request, 'vocabulary/detail.html', context)


def json(request, vocab_node_id):
    vocab = get_vocab(request.user, vocab_node_id)
    json_data = dumps(vocab_to_dict(vocab, 0), indent=4)
    return HttpResponse(json_data, content_type='application/json')


def export(vocab, data, extension, mime):
    timestamp = datetime.today().strftime('%Y-%m-%d')
    response = HttpResponse(data, content_type=mime)
    response['Content-Disposition'] = 'attachment; filename="%s-%s.%s"' % (
        vocab.node_id,
        timestamp,
        extension,
    )
    return response


@login_required
def skos(request, vocab_node_id):
    vocab = get_vocab(request.user, vocab_node_id)
    return export(vocab, export_skos(vocab), 'xml', 'application/rdf+xml')


@login_required
def csv(request, vocab_node_id):
    vocab = get_vocab(request.user, vocab_node_id)
    return export(vocab, export_csv(vocab), 'csv', 'text/comma-separated-values')


@ajax_login_required
def ordering(request, vocab_node_id):
    """Child concepts are ordered by ID if no order is specified.

    This view allows to set new ordering using concept.order.

    Request POST will look like:
        {'order-concept-478[]': ['2', '1', '3']} or
        {'order-vocab-15[]': ['1', '2', '5'...
    Where 478 is parent concept PK and 2, 1, 3 is new ordering
    of the children to rewrite their starting sequence 1, 2, 3.
    Ordering sequence numbers are not the same thing as concept.order

    Ordering the 1st level differs as instead of parent concept PK we get a vocab PK.
    """

    x = 'Order concepts'
    if request.method == 'POST':
        post_data = dict(request.POST)
        del post_data['csrfmiddlewaretoken']
        seq = [b[0] for a, b in post_data.items()]
        orderword_modelword_pk = list(post_data)[0]
        orderword, modelword, pk = orderword_modelword_pk.split('-')
        pk = int(pk.replace('[]', ''))
        if modelword == 'concept':
            model = Concept
            o = get_object_or_404(model, pk=pk)
            o = o.mother()
        else:
            model = Vocabulary
            o = get_object_or_404(model, pk=pk)
        children = dict(enumerate(o.get_children(), start=1))  # old order
        sequence = list(enumerate([int(x) for x in seq], start=1))  # new order mapping
        # print(children)  # >>> {1: <Concept: CSS>, 2: <Concept: JS>, 3: <Concept: HTML>}
        # print(sequence)  # >>> [(1, 3), (2, 1), (3, 2)]  # desired order HTML, CSS, JS
        for new_concept_order, forloop_counter in sequence:
            concept = children[forloop_counter]
            concept.order = new_concept_order
            concept.save()
        x = 'Updated order'
    return HttpResponse(x)


def vocabulary_edit(request, vocab_node_id):
    vocab = get_vocab(request.user, vocab_node_id)
    form = VocabularyForm(instance=vocab, label_suffix='')
    if not has_pro(vocab.user) and not vocab.private:
        form.fields['private'].widget.attrs['disabled'] = True

    predicates = vocab.predicates.all()
    if not predicates:
        predicates = ['addfirst']
    FormSet = inlineformset_factory(
        Vocabulary,
        Vocabulary.predicates.through,
        fk_name='vocabulary',
        form=PredicatesForm,
        extra=1,
        can_delete=True,
    )
    formset = FormSet(instance=vocab, prefix='pf')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/')
        else:
            form = VocabularyForm(request.POST, instance=vocab)
            formset = FormSet(request.POST, instance=vocab, prefix='pf')
            if form.is_valid():
                form.save()
            if formset.is_valid():
                formset.save()
            return redirect(vocab.get_absolute_url())
    context = {
        'vocabulary': vocab,
        'children': vocab.get_children(),
        'form': form,
        'formset': formset,
        'forms_and_set': zip(formset.forms, predicates, strict=False),
    }
    return render(request, 'vocabulary/vocabulary-edit.html', context)


@ajax_login_required
def concept_new(request, vocab_node_id, node_id=0):
    vocab = get_vocab(request.user, vocab_node_id)
    c = Concept(vocabulary=vocab)
    if vocab_node_id:
        parent = vocab
        add_parent = False
    if node_id:
        parent = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
        add_parent = True
    form = NewChildConceptForm(instance=c)
    if request.method == 'POST':
        form = NewChildConceptForm(request.POST, instance=c, label_suffix='')
        if form.is_valid():
            c = form.save()
            if add_parent:
                c.parent.add(parent)
            c.save()
            return redirect(parent.get_absolute_url())
    return render(
        request, 'vocabulary/new-concept.html', {'concept': c, 'parent': parent, 'form': form}
    )


def concept_edit(request, vocab_node_id, node_id):
    vocab = get_vocab(request.user, vocab_node_id)
    predicates = [('', 'Related')] + [(p.pk, p.name) for p in vocab.predicates.all()]
    c = get_object_or_404(Concept, node_id=node_id, vocabulary=vocab)
    children = c.get_children()
    related = c.related.all()
    if not related:
        related = ['addfirst']
    RelatedFormSet = inlineformset_factory(
        Concept,
        Concept.related.through,
        formset=BaseRelatedFormSet,
        fk_name='subject',
        form=RelatedForm,
        extra=1,
        can_delete=True,
    )
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/')
        else:
            form = ConceptForm(request.POST, instance=c)
            formset = RelatedFormSet(request.POST, instance=c, prefix='rf', predicates=predicates)
            if form.is_valid():
                form.save()
            if formset.is_valid():
                formset.save()
            return redirect(c.get_absolute_url())
    else:
        form = ConceptForm(instance=c, label_suffix='')
        formset = RelatedFormSet(instance=c, prefix='rf', predicates=predicates)
    context = {
        'children': children,
        'concept': c,
        'form': form,
        'formset': formset,
        'forms_and_set': zip(formset.forms, related, strict=False),
    }
    return render(request, 'vocabulary/concept-edit.html', context)


@ajax_login_required
def concept_adopt(request):
    if request.method != 'POST':
        raise Http404('post only')

    def get_objs(node_ids):
        if not node_ids:
            raise Http404('no data')
        vocab_node_id, node_id = node_ids.split(':')
        vocab = get_vocab(request.user, vocab_node_id)

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
            d.save()

    return HttpResponse('ok')


@ajax_login_required
def concept_del(request, vocab_node_id, node_id):
    vocab = get_vocab(request.user, vocab_node_id)

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
    vocab = get_vocab(request.user, vocab_node_id)

    allowed = False
    if request.user == vocab.user or request.user.is_staff:
        allowed = True
        if request.method == 'POST':
            if 'understand' in request.POST:
                vocab.delete()
                messages.success(request, f'"{vocab.title}" is now deleted.')
                return redirect('/tree/')
            messages.info(request, 'Not deleted. You need to tick the box to confirm.')
            return redirect(vocab.get_absolute_url())
    return render(
        request, 'vocabulary/vocabulary-delete.html', {'vocabulary': vocab, 'allowed': allowed}
    )
