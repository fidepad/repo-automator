from django.utils.deprecation import MiddlewareMixin


class CommonMiddleware(MiddlewareMixin):
    """This middleware adds common some useful attributes to the request object."""

    def process_request(self, request):
        # Add domain to request
        domain = "{}://{}".format(request.scheme, request.get_host())
        request.domain = domain
