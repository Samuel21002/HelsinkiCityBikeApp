from django.urls import path
from .views import load_csvimport_page, upload_file

app_name='csvimport'

urlpatterns = [
    path('', load_csvimport_page, name='csvimport'),
    path('upload/', upload_file, name='upload_file')
]
