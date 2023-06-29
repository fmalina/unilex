import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from lxml.html import fromstring, tostring
from transliterate import translit, utils as err


def is_url(text):
    if " " in text:
        return False
    if any(ord(char) > 127 for char in text):
        return False
    parts = text.split("/")
    if len(parts) and "." not in parts[0]:
        return False
    return True


def get_lang(dom):
    try:
        lang = dom.cssselect('html')[0].get('lang')
        if lang:
            return lang.split('-')[0].split('_')[0]
    except IndexError:
        pass
    return


@login_required
def translit_view(request, s):
    url = is_url(s)
    lang = None
    if url and request.user.subscription.is_active:
        u = f'https://{s}'
        s = requests.get(u, timeout=5).content.decode()
        dom = fromstring(s)
        lang = get_lang(dom)
        dom.make_links_absolute(u)
        s = tostring(dom, encoding='utf8').decode()
    elif url:
        s = 'Plus members only feature'
    try:
        result = translit(s, language_code=lang, reversed=True)
    except err.LanguageDetectionError:
        result = 'Language detection error'
    except err.LanguagePackNotFound:
        result = 'Language pack not found'
    if url:
        return HttpResponse(result)
    return render(request, 'translit.html', {
        'original': s,
        'result': result,
    })
