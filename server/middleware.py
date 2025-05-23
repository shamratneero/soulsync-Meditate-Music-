from django.utils.deprecation import MiddlewareMixin

class DisableCSRFOnAPIMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/musix/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
