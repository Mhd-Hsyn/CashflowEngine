from django.urls import path
from .views import (
    UploadLookupTableView
)

urlpatterns = [
    path('upload-lookup/', UploadLookupTableView.as_view(), name='upload-lookup'),
]

