from django.db import models
from utils.models.base import CreatedModel, TimeStampedModel

class MortalityRate(TimeStampedModel):
    """
    Stores the probability of death (qx) for each age.
    Sourced from lookup_probability.csv.
    """
    age = models.IntegerField(unique=True, db_index=True)
    qx = models.FloatField(help_text="Probability of death")
    px = models.FloatField(help_text="Probability of survival")

    class Meta:
        ordering = ['age']

    def __str__(self):
        return f"Age {self.age} - qx: {self.qx}"


