from rest_framework.serializers import (
    Serializer,
    FileField,
    ValidationError,
    ModelSerializer,
    SerializerMethodField
)
from .models import (
    CalculationJob, 
    JobAssumption, 
    EmployeeProjection
)


class FileUploadSerializer(Serializer):
    file = FileField()

    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise ValidationError("Only CSV files are allowed.")
        return value




class CalculationRequestSerializer(ModelSerializer):
    class Meta:
        model = CalculationJob
        fields = ['input_file', 'assumptions_file']


class AssumptionSerializer(ModelSerializer):
    class Meta:
        model = JobAssumption
        fields = ['valuation_date', 'discount_rate', 'salary_increase_rate', 'retirement_age']


class ProjectionSerializer(ModelSerializer):
    class Meta:
        model = EmployeeProjection
        fields = ['emp_id', 'emp_name', 'year', 'projected_salary', 'probability_qx', 'expected_outflow']


class CalculationResultSerializer(ModelSerializer):
    download_url = SerializerMethodField()
    assumptions = AssumptionSerializer(read_only=True)

    class Meta:
        model = CalculationJob
        fields = [
            'id', 'status', 'created_at', 
            'total_input_rows', 'total_output_rows', 
            'download_url', 'error_message',
            'assumptions'
        ]

    def get_download_url(self, obj):
        return obj.output_file.url if obj.output_file else None

