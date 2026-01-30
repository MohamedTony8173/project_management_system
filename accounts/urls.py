from django.urls import path 
from .views import RegisterAccount

app_name = 'accounts'

urlpatterns = [
    path('register/',RegisterAccount.as_view(),name='register')
]
