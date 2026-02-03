from django.urls import path 
from .views import NotificationListView,MakeReadNotificationsView

app_name = 'notifications'

urlpatterns = [
    path('list/',NotificationListView.as_view(),name='notification_list'),
    path('list/<int:notification_id>/',MakeReadNotificationsView.as_view(),name='notification_mark'),
]
