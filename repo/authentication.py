from drf_spectacular.extensions import OpenApiAuthenticationExtension
from knox.auth import TokenAuthentication


class KnoxAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = TokenAuthentication
    name = "KnoxAuthenticationScheme"  # name used in the schema
    priority = 1

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Value should be formatted: `Token <key>`",
        }
