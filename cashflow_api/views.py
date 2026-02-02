from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from .serializers import FileUploadSerializer
from .services import MortalityRateService
from core.utils.helpers import handle_serializer_exception

class UploadLookupTableView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            try:
                message = MortalityRateService.import_mortality_table(uploaded_file)
                return Response({
                    "status": True,
                    "message": message
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": False,
            "message": handle_serializer_exception(serializer)
        }, status=status.HTTP_400_BAD_REQUEST)



