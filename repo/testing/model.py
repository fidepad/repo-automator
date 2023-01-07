from rest_framework.test import APITestCase


class BaseModelTestCase(APITestCase):
    """Base test class for Model tests.

    This class serves as a base for all model test classes and provides
    common functionality for testing models, such as helper methods for
    creating and deleting test model instances, and assert functions for
    validating model attributes and behavior.
    """
