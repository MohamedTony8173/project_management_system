from django.urls import path 
from .views import ProjectIndex,ProjectListView,ProjectNearDueListView,ProjectDetailView

app_name = 'projects'

urlpatterns = [
    path('index/',ProjectIndex.as_view(),name='pro_index'),
    path('list/',ProjectListView.as_view(),name='pro_list'),
    path('list/due/',ProjectNearDueListView.as_view(),name='pro_due_list'),
    path('detail/<uuid:pk>/',ProjectDetailView.as_view(),name='project_detail'),
]
