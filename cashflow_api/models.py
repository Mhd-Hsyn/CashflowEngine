from django.db import models
from core.models.base import TimeStampedModel
from core.constants.choices import JobStatusChoices

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


class CalculationJob(TimeStampedModel):
    input_file = models.FileField(upload_to='inputs/data/')
    assumptions_file = models.FileField(upload_to='inputs/assumptions/')

    output_file = models.FileField(upload_to='outputs/', null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=JobStatusChoices.choices,
        default=JobStatusChoices.PENDING
    )
    error_message = models.TextField(null=True, blank=True)
    
    total_input_rows = models.IntegerField(default=0)
    total_output_rows = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.pk} - {self.get_status_display()}"
    
class JobAssumption(TimeStampedModel):
    job = models.OneToOneField(
        CalculationJob, on_delete=models.CASCADE, related_name='assumptions'
    )
    valuation_date = models.DateField()
    discount_rate = models.DecimalField(max_digits=10, decimal_places=6)
    salary_increase_rate = models.DecimalField(max_digits=10, decimal_places=6)
    retirement_age = models.IntegerField()

    def __str__(self):
        return f"Assumptions for Job {self.job_id}"


class EmployeeProjection(TimeStampedModel):
    job = models.ForeignKey(
        CalculationJob, on_delete=models.CASCADE, related_name='projections'
    )
    
    emp_id = models.CharField(max_length=50)
    emp_name = models.CharField(max_length=255, null=True, blank=True)
    
    year = models.IntegerField(help_text="Projected Year/Age")
    projected_salary = models.DecimalField(max_digits=20, decimal_places=2)
    probability_qx = models.DecimalField(max_digits=10, decimal_places=6)
    expected_outflow = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        ordering = ['emp_id', 'year']
        indexes = [
            models.Index(fields=['job', 'emp_id']),
        ]

