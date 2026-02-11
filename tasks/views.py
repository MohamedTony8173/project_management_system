from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
)

from comments.forms import CommentForm
from comments.models import Comment
from notifications.task import create_task_notification
from projects.models import Project
from .models import Task
from .forms import TaskFormCreation
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
import json
from django.db.models import Q
from django.http import Http404


class TaskCreateIndex(CreateView):
    model = Task
    form_class = TaskFormCreation
    success_url = reverse_lazy("accounts:dashboard")
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

            create_task_notification.delay(
                actor_name=actor, verb=verb, object_id=obj_id
            )
            return redirect(self.success_url)
        else:
            messages.error(self.request, "user has no permission to create")
            return redirect(self.request.path_info)


class TaskListView(ListView):
    model = Task
    template_name = "tasks/tasks_list.html"
    context_object_name = "tasks"
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        tasks = Task.objects.filter(Q(owner=user) | Q(team__member=user)).distinct()
        return tasks


class TaskNearDueListView(ListView):
    def get_queryset(self):
        user = self.request.user
        tasks_near = (
            Task.objects.due_t_or_less()
            .filter(Q(owner=user) | Q(team__member=user))
            .distinct()
        )
        return tasks_near

    model = Task
    template_name = "tasks/tasks_near_list.html"
    context_object_name = "tasks"
    paginate_by = 6


class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        comments = Comment.objects.filter_by_instance_model(task)
        context["comments"] = comments
        paginator = Paginator(comments, 3)

        page_number = self.request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context["page_obj"] = page_obj
        context["form_comment"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        if request.user not in task.team.member.all():
            messages.error(request, "You do not have access to comment on this task.")
            return redirect("tasks:task_detail", pk=task.id)

        form = CommentForm(request.POST)
        if form.is_valid():
            form_comment = form.save(commit=False)
            form_comment.user = request.user
            form_comment.content_object = task
            form_comment.save()

            # send notification
            actor = self.request.user.username
            verb = f"Comment on {task.name} Writing By {actor}"
            obj_id = task.id

            create_task_notification.delay(
                actor_name=actor, verb=verb, object_id=obj_id
            )
            messages.success(request, "Comment posted successfully!")
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{errors[0]}")

        return redirect("tasks:task_detail", pk=task.id)


@require_POST
def update_task_ajax(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.user not in task.team.member.all():
        return JsonResponse(
            {
                "success": False,
                "redirect_url": reverse(
                    "projects:kanban_dashboard", args=[task.project.id]
                ),
                "error": "You do not have permission to update this task.",
            }
        )

    data = json.loads(request.body)
    new_status = data.get("status").title()

    if new_status in ["Backlog", "To Do", "In Progress", "Completed"]:
        task.status = new_status
        task.save()
        return JsonResponse(
            {
                "success": True,
                "message": "Updated Success",
                "redirect_url": reverse(
                    "projects:kanban_dashboard", args=[task.project.id]
                ),
            }
        )
    else:
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid Status",
                "redirect_url": reverse(
                    "projects:kanban_dashboard", args=[task.project.id]
                ),
            },
            status=400,
        )


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "tasks/task_delete.html"
    context_object_name = "task"

    def get_object(self, queryset=None):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        if task.owner != self.request.user:
            raise Http404("Not Access")
        return task

    def form_invalid(self, form):
        messages.error(self.request, "Invalid Input")
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Deleted Success")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:task_list")


class TaskEditView(UpdateView):
    model = Task
    template_name = "tasks/task_edit.html"
    context_object_name = "task"
    form_class = TaskFormCreation

    def get_object(self, queryset=None):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        if task.owner != self.request.user:
            raise Http404("Not Access")
        return task

    def form_invalid(self, form):
        messages.error(self.request, "Invalid Input")
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Updated Success")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:task_list")
