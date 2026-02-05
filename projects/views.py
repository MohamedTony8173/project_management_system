from django.contrib import messages
from django.shortcuts import redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView,DetailView

from notifications.task import create_notification
from projects.forms import ProjectFormCreation
from projects.models import Project
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from comments.forms import CommentForm




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
        project = self.get_object()
        if request.user not in project.team.member.all():
            messages.error(request, 'You do not have access to comment on this project.')
            return redirect('projects:project_detail', pk=project.id)

        form = CommentForm(request.POST)
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
            messages.success(request, 'Comment posted successfully!')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{errors[0]}")
                
        return redirect('projects:project_detail', pk=project.id)
   