from django.http import HttpResponsePermanentRedirect
from fregat.models import Redirect


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.get_full_path()

        if path:
            redirect = Redirect.objects.filter(source=path).first()
            if redirect:
                return HttpResponsePermanentRedirect(redirect.destination)

        return response


class FrontDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.front_data = {
            'topMenu': {},
            'geo': {},
            'contacts': {},
        }
        response = self.get_response(request)
        return response