from django.db import models
from projects.models import Project
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
from django.urls import reverse
from teams.models import Team

User = get_user_model()


class TaskQuery(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def upComing(self):
        return self.filter(due_date__gte=timezone.now())
    
    def due_in_tow_days_or_less(self):
        today = timezone.now().date()
        tow_todays = today + timezone.timedelta(days=2)
        return self.active().upComing().filter(due_date__lte=tow_todays)
    



class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuery(self.model, using=self._db)

    def all_upcoming(self):
        return self.get_queryset().active().upComing()
    
    def due_t_or_less(self):
        return self.get_queryset().due_in_tow_days_or_less()
    



class Task(models.Model):
    STATUS_CHOICE = (
        ("Backlog", "Backlog"),
        ("To Do", "To Do"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    )
    PRIORITY_CHOICE = (
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, verbose_name=_("owner"), on_delete=models.CASCADE, related_name="tasks"
    )
    team = models.ForeignKey(
        Team, verbose_name=_("team"), on_delete=models.CASCADE, related_name="tasks"
    )
    project = models.ForeignKey(
        Project,
        verbose_name=_("project"),
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICE, default="Backlog"
    )
    priority = models.CharField(
        _("priority"), max_length=20, choices=PRIORITY_CHOICE, default="Low"
    )
    active = models.BooleanField(_("active"), default=False)
    start_date = models.DateField(_("start date"))
    due_date = models.DateField(_("due date"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    update_at = models.DateTimeField(_("update at"), auto_now=True)
    objects = TaskManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at",)

    def get_due_date(self):
        if self.due_date:
            current_date = timezone.now().date()
            return (self.due_date - current_date).days
        else:
            return None

    def get_priority_color(self):
        if self.priority == "Low":
            color = "success"
        elif self.priority == "Medium":
            color = "warning"
        else:
            color = "danger"
        return color
    
    def get_progress_color(self):
        if self.status == "To Do":
            color = "muted"
        elif self.status == "In Progress":
            color = "primary"
        else:
            color = "success"
        return color

    @property
    def progress(self):
        progress_dict = {
            "To Do": 0,
            "In Progress": 50,
            "Completed": 100,
        }
        return progress_dict.get(self.status, 0)
    
    def get_absolute_url(self):
        return reverse("tasks:task_detail", kwargs={"pk": self.pk})
    
