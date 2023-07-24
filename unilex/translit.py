import requests
import requests_cache
import transliterate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from lxml import html

SITE = 'https://unilexicon.com/translit'
NAME = 'Unilexicon Translitera'
NOTE = f"""
<div id="translit" style="position:fixed;top:.5rem;right:.5rem;z-index:999;font-family:sans-serif;
    padding:.5rem 1rem;background-color:ivory;border-radius:3px;border:1px solid goldenrod;box-shadow:0 0 5px goldenrod">
    Transliterated with <a href="{SITE}" style="color:dodgerblue">{NAME}</a>
    <a href="#" onclick="return document.getElementById('translit').style.display = 'none'"
        style="color:gray;text-decoration:none;margin-left:.5rem">×</a>
</div>
"""

requests_cache.install_cache(
    cache_name='requests_cache', backend='sqlite',
    expire_after=30*24*3600)


def is_url(text):
    if " " in text:
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
        return
    return


def err(request, url, exception):
    return render(request, 'translit.html', {
        'exception': exception, 'redirect': SITE, 'url': url}, status=500)


@login_required
def translit_view(request, url):
    if not request.user.subscription.is_active:
        return redirect('subscribe')
    if not is_url(url):
        return err(request, url, 'Please, use a correct address.')
    session = requests.Session()
    session.headers.update({
        'User-agent': f'Mozilla/5.0 (compatible; {NAME}/0.1; +{SITE})'})
    try:
        response = session.get(f'https://{url}', timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return err(request, url, f'That website had an error: {e}')
    except requests.exceptions.Timeout:
        return err(request, url, 'That website timed out.')
    except requests.exceptions.TooManyRedirects:
        return err(request, url, 'That website redirected too many times.')
    except requests.exceptions.RequestException as e:
        return err(request, url, e)

    s = response.content.decode()
    dom = html.fromstring(s)
    lang = get_lang(dom)
    dom.make_links_absolute(f'https://{url}')
    dom.find(".//body").insert(0, html.fromstring(NOTE))
    s = html.tostring(dom, encoding='utf8').decode()

    try:
        result = transliterate.translit(s, language_code=lang, reversed=True)
        return HttpResponse(result)
    except transliterate.utils.LanguageDetectionError:
        return HttpResponse(s.replace(
            'Transliterated with',
            'Not transliterated, is this in latin script?'
        ))
    except transliterate.utils.LanguagePackNotFound:
        try:  # try without language set
            return HttpResponse(transliterate.translit(s, reversed=True))
        except Exception as e:
            return HttpResponse(s.replace(
                'Transliterated with',
                f'Not transliterated, {e}'
            ))
    return HttpResponse(s)
