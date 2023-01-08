from django.urls import path
from .views import load_index_page

app_name='core'

urlpatterns = [
    path('', load_index_page, name='index')
]
