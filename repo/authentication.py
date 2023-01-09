from drf_spectacular.extensions import OpenApiAuthenticationExtension
from knox.auth import TokenAuthentication


class KnoxAuthenticationScheme(OpenApiAuthenticationExtension):
    """An OpenAPI extension that adds a Knox authentication swagger docs."""
    target_class = TokenAuthentication
    name = "KnoxAuthenticationScheme"  # name used in the schema
    priority = 1

    def get_security_definition(self, auto_schema):
        """Get the security definition for the Knox authentication scheme.

        Parameters:
            auto_schema (AutoSchema): The AutoSchema instance to which the security definition will be added.

        Returns:
            dict: The security definition for the Knox authentication scheme.
        """
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Value should be formatted: `Token <key>`",
        }
