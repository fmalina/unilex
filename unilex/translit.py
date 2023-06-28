import requests
from django.http import HttpResponse, Http404
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
            return lang.split('-')[0]
    except IndexError:
        pass
    return


def translit_view(request, s):
    s = s.replace('http://', '').replace('https://', '')
    url = is_url(s)
    lang = None
    if url and 0:  # disable
        u = f'http://{s}'
        s = requests.get(u, timeout=5).content.decode()
        dom = fromstring(s)
        lang = get_lang(dom)
        dom.make_links_absolute(u)
        s = tostring(dom).decode()
    try:
        result = translit(s, language_code=lang, reversed=True)
    except (err.LanguageDetectionError, err.LanguagePackNotFound):
        raise Http404
    if url:
        return HttpResponse(result, status=404)
    return render(request, 'translit.html', {'content': result}, status=404)
