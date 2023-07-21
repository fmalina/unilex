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


maps = {
    'ru_xx': "а б в г д е ё ж з и й к л м н о п р с т у ф  х ц ч ш  щ ъ ы ь э  ю  я",
    'sk_ru': "a b v g d e é ž z i j k l m n o p r s t u f ch c č š šč ъ y ' é ju ja",
    'ka_xx': "ა ბ ვ გ დ ე ვ ზ თ ი კ ლ მ ნ ო პ რ ს ტ უ ფ ქ  ღ ყ შ ჩ ც  ძ  წ  ჭ  ხ ჯ ჰ",
    'sk_ka': "a b v g d e v z t i k l m n o p r s t u f k gh q š č c ts dz ts kh j h",
}


def translit_custom(request):
    txt = request.GET.get('txt', '')
    inp_map = request.GET.get('inp', '').split()
    out_map = request.GET.get('out', '').split()
    io_map = list(zip(inp_map, out_map))
    result = []
    for word in txt.split():
        for a, b in io_map:
            if word.isupper():
                word = word.lower().replace(a, b).upper()
            if word.istitle():
                word = word.lower().replace(a, b).title()
            else:
                word = word.replace(a, b)
            # word beginnings and endings
            if a.startswith('*') or a.endswith('*'):
                a = a.replace('*', '')
                if word.endswith(a) or word.endswith(a):
                    word = word.replace(a, b)
        result.append(word)
    new_a = []
    new_b = []
    for a, b in io_map:
        if len(b) > len(a): a = a.rjust(len(b))
        if len(a) > len(b): b = b.rjust(len(a))
        new_a.append(a)
        new_b.append(b)
    return render(request, 'translit.html', {
        'original': txt,
        'result': ' '.join(result),
        'inp_map': ' '.join(new_a),
        'out_map': ' '.join(new_b),
        'maps': {a: b.replace(' ', '+') for a, b in maps.items()}
    })


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
