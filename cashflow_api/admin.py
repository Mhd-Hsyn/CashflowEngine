from django.contrib import admin
from .models import (
    MortalityRate,
    CalculationJob,
    JobAssumption,
    EmployeeProjection
)




@admin.register(MortalityRate)
class MortalityRateAdmin(admin.ModelAdmin):
    search_fields = ('age', )
    list_display = ('age', 'qx_percent', 'qx_value', 'px_percent', 'px_value', 'created_at')


@admin.register(CalculationJob)
class CalculationJobAdmin(admin.ModelAdmin):
    search_fields = ('status', )
    list_display = ('status', 'input_file', 'output_file', 'total_input_rows', 'total_output_rows', 'created_at')


@admin.register(JobAssumption)
class JobAssumptionAdmin(admin.ModelAdmin):
    search_fields = ('job', )
    list_display = (
        'job', 'valuation_date', 'discount_rate', 
        'salary_increase_rate', 'retirement_age', 'created_at'
    )


@admin.register(EmployeeProjection)
class EmployeeProjectionAdmin(admin.ModelAdmin):
    search_fields = ('job', )
    list_display = (
        'job', 'emp_id', 'emp_name', 'year',  'projected_salary',  
        'probability_qx',  'expected_outflow',  'created_at'
    )
