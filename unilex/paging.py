"""
Generic pagination reusable at view level.

Paging middleware needs installing in the settings:

    MIDDLEWARE = (
        ... almost at the end...
        'paging.paging_middleware',

Use in a view like so:

    from unilex.paging import simple_paging

    def listings(request):
        ls = Listing.objects.all()
        ls, count, paging = simple_paging(request, ls, 100)
        return render(request, 'some_listings.html', {
            'ls': ls, 'count': count, 'paging': paging
            })

Include paging in your listings template:

    {{ paging }}

"""

from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404


def paging_middleware(get_response):
    def middleware(request):
        try:
            request.page = int(request.GET.get('page', 1))
        except ValueError as e:
            raise Http404('Page does not exist') from e
        return get_response(request)

    return middleware


def simple_paging(request, qs, limit):
    pager = Paginator(qs, limit)
    try:
        page_obj = pager.page(request.page)
        qs = page_obj.object_list
    except EmptyPage:
        page_obj = {}
        qs = qs.none()

    pages = pager.page_range
    count = pager.count

    paginate = render_paging(request, pages, page_obj, count, limit)

    return qs, count, paginate


def render_paging(request, pages, page_obj, count, limit):
    pages = sample(pages, request.page)

    get = request.GET.copy()
    get.pop('page', None)
    context = {
        'path': request.path_info,
        'pages': pages,
        'page_obj': page_obj,
        'is_paginated': count > limit,
        'getvars': '&' + get.urlencode() if get else '',
    }
    return render_to_string('pagination.html', context)


def sample(pages, current):
    """Show first few, few around the current page & a last page"""
    if len(pages) > 20:
        ls = []
        prev = False
        for x in pages:
            a = False
            if x in range(1, 5) or x in range(current - 5, current + 5) or x == pages[-1]:
                a = x
            if prev or a:
                ls.append(a)
            prev = a
        pages = ls
    return pages
