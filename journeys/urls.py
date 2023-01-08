from django.urls import path
from .views import load_journeys_page

app_name='journeys'

urlpatterns = [
    path('', load_journeys_page, name='journeys')
]
