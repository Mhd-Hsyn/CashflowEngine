from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    CalculationJob
)
from .serializers import (
    FileUploadSerializer,
    CalculationRequestSerializer,
    CalculationResultSerializer,
)
from .services import (
    MortalityRateService,
    CalculationEngine
)
from core.utils.helpers import (
    handle_serializer_exception
)


class UploadLookupTableView(APIView):

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


class RunCalculationView(APIView):

    def post(self, request):
        serializer = CalculationRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            job = serializer.save()
            
            try:
                engine = CalculationEngine(job.id)
                engine.run()
                
                job.refresh_from_db()
                return Response(
                    CalculationResultSerializer(job).data, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                 return Response({
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": False,
            "message": handle_serializer_exception(serializer)
        }, status=status.HTTP_400_BAD_REQUEST)


class CalculationHistoryView(APIView):

    def get(self, request):
        jobs = CalculationJob.objects.all()
        serializer = CalculationResultSerializer(jobs, many=True)
        return Response(serializer.data)


