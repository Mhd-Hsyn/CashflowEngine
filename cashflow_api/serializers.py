from rest_framework.serializers import (
    Serializer,
    FileField,
    ValidationError
)



class FileUploadSerializer(Serializer):
    file = FileField()

    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise ValidationError("Only CSV files are allowed.")
        return value


