from django.shortcuts import render
from django.http import HttpResponse
from transliterate import translit
from transliterate.utils import LanguageDetectionError
import requests


def handle404(request, exception):
    return render(request, '404.html', {'exception': exception})


def translit_view(request, s):
    try:
        if '.' in s and ' ' not in s:
            url = f'https://{s}'
            if url:
                response = requests.get(url)
                body = response.content.decode()
                result = translit(body, reversed=True)
        else:
            result = translit(s, reversed=True)
    except LanguageDetectionError:
        return handle404(request, exception=None)

    return HttpResponse(result)
