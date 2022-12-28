from django.db import models


class BaseModel(models.Model):
    """Base Model to reduce redundant columns below."""

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class for Base Model."""

        abstract = True
