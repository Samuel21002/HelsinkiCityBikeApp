from django.urls import path
from .views import load_journeys_page, get_journey_info, search_journey


app_name='journeys'

urlpatterns = [
    path('', load_journeys_page, name='journeys'),
    path('get_journey_info/<int:id>', get_journey_info, name='get_journey_info'),
    path('search_journeys/', search_journey, name='search_journeys'),
]
