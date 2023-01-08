from django.utils.deprecation import MiddlewareMixin


class CommonMiddleware(MiddlewareMixin):
    """This middleware adds common some useful attributes to the request
    object."""

    def process_request(self, request):
        """Add the domain attribute to the request object."""
        # Add domain to request
        domain = f"{request.scheme}://{request.get_host()}"
        request.domain = domain
