from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView,DetailView

from notifications.task import create_notification
from projects.forms import ProjectFormCreation
from projects.models import Project


class ProjectIndex(CreateView):
    model = Project
    form_class = ProjectFormCreation
    success_url = reverse_lazy("homeApp:home")
    template_name = "projects/index.html"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            obj = form.save(commit=False)
            obj.owner = self.request.user
            obj.save()

            # send notification
            actor = self.request.user.username
            verb = f"Project {obj.name} was Assigned"
            obj_id = obj.id

            create_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
            return redirect(self.success_url)
        else:
            messages.error(self.request, "user has no permission to create")
            return redirect(self.request.path_info)


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 6


class ProjectNearDueListView(ListView):
    def get_queryset(self):
        super().get_queryset()
        projects_near = Project.objects.due_t_or_less()
        return projects_near

    model = Project
    template_name = "projects/project_near_list.html"
    context_object_name = "projects"
    paginate_by = 6


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"