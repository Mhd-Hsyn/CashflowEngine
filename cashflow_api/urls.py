from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UploadLookupTableView,
    RunCalculationView,
    CalculationHistoryViewset,
)

calculation_router = DefaultRouter()
calculation_router.register(r'calculations-history', CalculationHistoryViewset, basename='calculations_history')


urlpatterns = [
    path('upload-lookup/', UploadLookupTableView.as_view(), name='upload-lookup'),
    path('run-calculation/', RunCalculationView.as_view(), name='run-calculation'),
    path('', include(calculation_router.urls)),

]

