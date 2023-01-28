from django.urls import path
from .views import load_stations_page, render_geojson, get_station_info, get_station_names

app_name='stations'

urlpatterns = [
    path('', load_stations_page, name='stations'),
    path('render_geojson', render_geojson, name='render_geojson'),
    path('get_station_names', get_station_names, name='get_station_names'),
    path('get_station_info/<int:station_id>/<str:month>', get_station_info, name='get_station_info')
]
