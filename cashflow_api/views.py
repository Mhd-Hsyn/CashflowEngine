from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework import status
from .models import (
    CalculationJob,
    EmployeeProjection
)
from .serializers import (
    FileUploadSerializer,
    CalculationRequestSerializer,
    CalculationResultSerializer,
    ProjectionSerializer
)
from .services import (
    MortalityRateService,
    CalculationEngine,
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
                return Response({
                    "status": True,
                    "data": CalculationResultSerializer(job).data, 
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                 return Response({
                    "status": False,
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": False,
            "message": handle_serializer_exception(serializer)
        }, status=status.HTTP_400_BAD_REQUEST)


class CalculationHistoryViewset(GenericViewSet):

    @action(detail=False, methods=['GET'], url_path='retrive')
    def get_all_calculations(self, request):

        page_number = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        offset = (page_number - 1) * page_size
        jobs = CalculationJob.objects.all()[offset:offset + page_size + 1]

        has_next = len(jobs) > page_size
        has_previous = page_number > 1
        serializer = CalculationResultSerializer(jobs[:page_size], many=True)

        return Response({
            "status": True,
            "has_next": has_next,
            "has_previous": has_previous,
            "page_number": page_number,
            "page_size": page_size,
            "data": serializer.data
        },status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path='projections')
    def get_projections(self, request):
        job_id = request.query_params.get("job_id", None)
        if not job_id:
            return Response({
                "status": False,
                "message": "job_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        projections = EmployeeProjection.objects.filter(job=job_id).order_by('emp_id', 'year')

        serializer = ProjectionSerializer(projections, many=True)
        
        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


