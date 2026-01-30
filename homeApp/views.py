from django.shortcuts import render
from django.views.generic import View

from accounts.models import Profile
from notifications.models import Notification
from projects.models import Project
from tasks.models import Task

class HomeIndex(View):
    def get(self,request):
        context = {
            "projects" : Project.objects.all()[:5],
            "tasks" : Task.objects.all()[:5],
            "profiles" : Profile.objects.all()[:5],
            "notifications" : Notification.objects.get_user_notification(request.user)[:3],
        }
        return render(request,'homeApp/index.html',context)
    

