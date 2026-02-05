from django.urls import path 
from .views import TaskCreateIndex,TaskListView,TaskNearDueListView,TaskDetailView
app_name = 'tasks'

urlpatterns = [
    path('create/',TaskCreateIndex.as_view(),name='task_create'),
    path('list/',TaskListView.as_view(),name='task_list'),
    path('list/due/',TaskNearDueListView.as_view(),name='task_due_list'),
    path('detail/<uuid:pk>/',TaskDetailView.as_view(),name='task_detail'),
]
