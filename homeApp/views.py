from django.shortcuts import render
from django.views.generic import View

from accounts.models import Profile
from notifications.models import Notification
from projects.models import Project
from tasks.models import Task
from teams.models import Team


class HomeIndex(View):
    def get(self, request):

        tasks_count = Task.objects.all().active().count()
        task_in_progress = Task.objects.all().filter(status="In Progress").count()
        task_completed = Task.objects.all().filter(status="Completed").count()

        projects = Project.objects.all().active().count()
        project_in_progress = Project.objects.all().filter(status="In Progress").count()
        projects_completed = Project.objects.all().filter(status="Completed").count()

        if tasks_count > 0:
            task_percentage = (task_completed / tasks_count) * 100
        else:
            task_percentage = 0

        if projects > 0:
            project_percentage = (projects_completed / projects) * 100
        else:
            project_percentage = 0

        teams = Team.objects.all().count()
        
        if teams > 0:
            team_percentage = (projects_completed / teams ) * 100
        else:
            team_percentage = 0

        context = {
            "projects": Project.objects.all()[:5],
            "tasks": Task.objects.all()[:5],
            "profiles": Profile.objects.all()[:5],
            "project_in_progress": project_in_progress,
            "projects_completed": projects_completed,
            "project_percentage": project_percentage,
            "task_in_progress": task_in_progress,
            "tasks_count": tasks_count,
            "task_percentage": task_percentage,
            "task_completed": task_completed,
            "teams": teams,
            'team_percentage':team_percentage
        }

        if request.user.is_authenticated:
            notifications = Notification.objects.get_user_notification(request.user)[:3]
            context["notifications"] = notifications
        return render(request, "homeApp/index.html", context)
