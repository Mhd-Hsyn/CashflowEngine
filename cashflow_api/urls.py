from django.urls import path
from .views import (
    UploadLookupTableView,
    RunCalculationView,
    CalculationHistoryView,
)

urlpatterns = [
    path('upload-lookup/', UploadLookupTableView.as_view(), name='upload-lookup'),
    path('run-calculation/', RunCalculationView.as_view(), name='run-calculation'),
    path('history/', CalculationHistoryView.as_view(), name='calculation-history'),
]

