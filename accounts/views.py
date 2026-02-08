from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from accounts.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_not_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.forms import RegisterUserForm
from .tokens import account_activation_token
from django.shortcuts import render
from django.views.generic import View

from projects.models import Project
from tasks.models import Task
from teams.models import Team


@login_not_required
def account_login(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    user = authenticate(request, email=email, password=password)
    remember_me = request.POST.get("remember_me")
    if user is not None:
        if remember_me:
            request.session.set_expiry(1209600)
        else:
            request.session.set_expiry(0)
        login(request, user)
        return redirect("accounts:dashboard")
    return render(request, "accounts/registrations/login.html")


def account_logout(request):
    logout(request)
    messages.success(request, "Logged Out")
    return redirect("accounts:dashboard")


User = get_user_model()


@login_not_required
def send_user_email(request, user):
    current_site = get_current_site(request).domain
    protocol = "http"
    subject = "Activate your account"

    context = {
        "user": user,
        "protocol": protocol,
        "domain": current_site,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    }

    body = render_to_string("accounts/registrations/email_.html", context)

    email = EmailMessage(subject, body, "admin@site.com", [user.email])
    email.send(fail_silently=False)


@login_not_required
def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_user_email(request, user)
            messages.success(
                request, "Please check your email to activate your account."
            )
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid input")
    else:
        form = RegisterUserForm()
    return render(request, "accounts/registrations/register.html", {"form": form})


@login_not_required
def email_activated(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated!")
        return redirect("accounts:dashboard")
    else:
        messages.error(request, "The activation link is invalid or has expired.")
    return redirect("accounts:dashboard")


class ProfileList(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "accounts/profile/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 6


class DashboardView(View):
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
            team_percentage = (projects_completed / teams) * 100
        else:
            team_percentage = 0

        context = {
            "projects": Project.objects.due_t_or_less()[:5],
            "projects_counts": Project.objects.all(),
            "tasks": Task.objects.due_t_or_less()[:5],
            "profiles": Profile.objects.all()[:4],
            "project_in_progress": project_in_progress,
            "projects_completed": projects_completed,
            "project_percentage": project_percentage,
            "task_in_progress": task_in_progress,
            "tasks_count": tasks_count,
            "task_percentage": task_percentage,
            "task_completed": task_completed,
            "teams": teams,
            "team_percentage": team_percentage,
        }

        return render(request, "accounts/dashboard.html", context)
