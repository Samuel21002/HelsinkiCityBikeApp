from django.urls import path
from .views import load_stations_page

app_name='stations'

urlpatterns = [
    path('', load_stations_page, name='stations')
]
