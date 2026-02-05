from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView,DetailView

from comments.forms import CommentForm
from comments.models import Comment
from notifications.task import create_task_notification
from .models import Task
from .forms import TaskFormCreation
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage


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

        page_number = self.request.GET.get('page')
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
            messages.error(request, 'You do not have access to comment on this task.')
            return redirect('tasks:task_detail', pk=task.id)

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

            create_task_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
            messages.success(request, 'Comment posted successfully!')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{errors[0]}")
                
        return redirect('tasks:task_detail', pk=task.id)
   