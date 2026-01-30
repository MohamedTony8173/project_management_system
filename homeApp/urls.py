from django.urls import path 
from .views import HomeIndex

app_name = 'homeApp'

urlpatterns = [
    path('',HomeIndex.as_view(),name='home')
]
