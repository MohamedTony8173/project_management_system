from django.urls import path 
from .views import ProjectIndex

app_name = 'projects'

urlpatterns = [
    path('index',ProjectIndex.as_view(),name='pro_index')
]
