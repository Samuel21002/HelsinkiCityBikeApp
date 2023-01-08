from django.urls import path
from .views import load_csvimport_page

app_name='csvimport'

urlpatterns = [
    path('', load_csvimport_page, name='csvimport')
]
