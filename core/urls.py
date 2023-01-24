from django.urls import path
from .views import load_index_page, login, logout, loader, celery_progress_terminate

app_name='core'

urlpatterns = [
    path('', load_index_page, name='index'),
    path('login/', login, name='login'),
    path('loader/', loader, name='loader'),
    path('logout/', logout, name='logout'),
    path('celery_progress_terminate/<str:task_id>', celery_progress_terminate, name='terminate'),
]
