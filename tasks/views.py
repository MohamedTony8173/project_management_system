from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from notifications.task import create_task_notification
from .models import Task
from .forms import TaskFormCreation


class TaskCreateIndex(CreateView):
    model = Task
    form_class = TaskFormCreation
    success_url = reverse_lazy("homeApp:home")
    template_name = "tasks/create.html"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            obj = form.save(commit=False)
            obj.owner = self.request.user
            obj.save()

            # send notification
            actor = self.request.user.username
            verb = f"Task {obj.name} was Assigned"
            obj_id = obj.id

            create_task_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
            return redirect(self.success_url)
        else:
            messages.error(self.request, "user has no permission to create")
            return redirect(self.request.path_info)


class TaskListView(ListView):
    model = Task
    template_name = "tasks/tasks_list.html"
    context_object_name = "tasks"
    paginate_by = 6


class TaskNearDueListView(ListView):
    def get_queryset(self):
        super().get_queryset()
        tasks_near = Task.objects.due_t_or_less()
        return tasks_near

    model = Task
    template_name = "tasks/tasks_near_list.html"
    context_object_name = "tasks"
    paginate_by = 6
