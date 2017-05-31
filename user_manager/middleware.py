from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile

EXEMPT_URLS = [compile('accounts/login')]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        path = request.path_info.lstrip('/')
        if not request.user.is_authenticated() and not any(m.match(path) for m in EXEMPT_URLS):
            return HttpResponseRedirect('/accounts/login')

        # Code to be executed for each request/response after
        # the view is called.

        return response