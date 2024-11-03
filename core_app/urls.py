from django.urls import path
from .views import download_file

urlpatterns = [
    # other urls
    path('download/<int:file_pk>/', download_file, name='download_file'),
]