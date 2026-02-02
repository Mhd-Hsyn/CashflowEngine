from django.db import models
from core.models.base import TimeStampedModel

class MortalityRate(TimeStampedModel):
    age = models.IntegerField(unique=True, db_index=True)

    qx_percent = models.DecimalField(max_digits=10, decimal_places=6, help_text="Probability of death")
    qx_value = models.DecimalField(max_digits=10, decimal_places=6)
    px_percent = models.DecimalField(max_digits=10, decimal_places=6, help_text="Probability of survival")
    px_value = models.DecimalField(max_digits=10, decimal_places=6)


    class Meta:
        ordering = ['age']

    def __str__(self):
        return f"Age {self.age} - qx: {self.qx_percent}"


