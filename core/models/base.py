import uuid
from django.db import models


class CreatedModel(models.Model):
    """Base model with only created_at timestamp, for immutable records."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampedModel(CreatedModel):
    """Base model with created_at and updated_at timestamps, for auditable records."""
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

