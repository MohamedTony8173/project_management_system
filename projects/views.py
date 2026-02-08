from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from notifications.task import create_notification,create_task_notification
from projects.forms import ProjectFormCreation, AttachForm
from projects.models import Project
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from comments.forms import CommentForm
from tasks.forms import TaskFormCreationModel
from tasks.models import Task

from django.utils import timezone


class ProjectIndex(CreateView):
    model = Project
    form_class = ProjectFormCreation
    success_url = reverse_lazy("accounts:dashboard")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        comments = Comment.objects.filter_by_instance_model(project)
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
        context["form_attach"] = AttachForm()
        return context

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user not in project.team.member.all():
            messages.error(
                request, "You do not have access on this project."
            )
            return redirect("projects:project_detail", pk=project.id)

        form = CommentForm(request.POST)
        if "comment_submit" in request.POST:
            if form.is_valid():
                form_comment = form.save(commit=False)
                form_comment.user = request.user
                form_comment.content_object = project
                form_comment.save()

                # send notification
                actor = self.request.user.username
                verb = f"Comment on {project.name} Writing By {actor}"
                obj_id = project.id

                create_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
                messages.success(request, "Comment posted successfully!")
            else:
                for field, errors in form.errors.items():
                    messages.error(request, f"{errors[0]}")

        if "attach_submit" in request.POST:
            form = AttachForm(request.POST, request.FILES)
            if form.is_valid():
                attach = form.save(commit=False)
                attach.project = project
                attach.user = request.user
                attach.save()
                # send notification
                actor = self.request.user.username
                verb = f"File was Uploaded on this {project.name}  By {actor}"
                obj_id = project.id
                create_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
                messages.success(request, "Upload file successfully!")
                return redirect("projects:project_detail", pk=project.id)
            else:
                for field, errors in form.errors.items():
                    messages.error(request, f"{errors[0]}")

        return redirect("projects:project_detail", pk=project.id)



class KanbanView(DetailView):
    model = Project
    template_name = "projects/kanban.html"
    context_object_name = "project"
    
    
    def get_context_data(self, **kwargs):
        project = self.get_object()
        context = super().get_context_data(**kwargs)
        context["task_backlog"] = project.tasks.filter(status='Backlog').upComing()
        context["task_to_do"] = project.tasks.filter(status='To Do').upComing()
        context["task_progress"] = project.tasks.filter(status='In Progress').upComing()
        context["task_completed"] = project.tasks.filter(status='Completed').upComing()
        context["form"] = TaskFormCreationModel()
        return context
    
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user not in project.team.member.all():
            messages.error(
                request, "You do not have access to Create Task on this project."
            )
            return redirect("projects:project_detail", pk=project.id)

        form = TaskFormCreationModel(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.owner = request.user
            task.team = project.team
            task.start_date = timezone.now()
            task.save()
            # send notification
            actor = request.user.username
            verb = f"Task {task.name} was Assigned"
            obj_id = task.id

            create_task_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
            messages.success(request,'Task Created!')
            return redirect("projects:kanban_dashboard", pk=project.id)
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{errors[0]}")

        return redirect("projects:kanban_dashboard", pk=project.id)

    
def update_task(request,pk):
    task = get_object_or_404(Task,id=pk)
    if request.method == 'POST':
        if request.user not in task.team.member.all(): 
            messages.error(
                request, "You do not have an access on this project."
            )
            return redirect("projects:project_detail", pk=task.project.id)
        
        if task.owner == request.user.username:
            messages.error(
                request, "You do not have an access on this project. you do not owner"
            )
            return redirect("projects:project_detail", pk=task.project.id)
            
        form = TaskFormCreationModel(request.POST,instance=task)
        if form.is_valid():
            form.save()
            # send notification
            actor = request.user.username
            verb = f"Task {task.name} was Updated"
            obj_id = task.id

            create_task_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)
            messages.success(request,'Task Updated!')
            return redirect("projects:kanban_dashboard", pk=task.project.id)
    else:
        form = TaskFormCreationModel(instance=task)
    context = {
        'form':form,
        'task':task
    }
    return render(request,"tasks/update_task.html", context)


