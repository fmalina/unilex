from django.http import HttpResponse
import string

def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        return HttpResponse('<p>Please login above to do more.</p>')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap 

def processTokens(tokens):
    ''' camelCase '''
    result='';
    for token in tokens:
        if token is not None:
            result=result+token.title()
    return result

def processString(string,separator=' '):
    li=string.split(separator)
    if li is not []:
        result=li[0]
        result=result+processTokens(li[1:])
    return result

def getCamelCase(string,separator=' '):
    return processString(string,separator)