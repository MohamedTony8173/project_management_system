from django.urls import path 
from .views import RegisterAccount,ProfileList

app_name = 'accounts'

urlpatterns = [
    path('register/',RegisterAccount.as_view(),name='register'),
    path('profile/list/',ProfileList.as_view(),name='profile_list'),
]
