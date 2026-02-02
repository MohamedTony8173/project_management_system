from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model

from teams.models import Team


User = get_user_model()


class ProjectQuery(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def upComing(self):
        return self.filter(due_date__gte=timezone.now())
    
    def due_in_tow_days_or_less(self):
        today = timezone.now().date()
        tow_todays = today + timezone.timedelta(days=2)
        return self.active().upComing().filter(due_date__lte=tow_todays)


class ProjectManager(models.Manager):
    def get_queryset(self):
        return ProjectQuery(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active().upComing()
    
    def due_t_or_less(self):
        return self.get_queryset().due_in_tow_days_or_less()


class Project(models.Model):
    STATUS_CHOICE = (
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
    team = models.ForeignKey(
        Team, verbose_name=_("team"), on_delete=models.CASCADE, related_name="projects"
    )
    owner = models.ForeignKey(
        User, verbose_name=_("owner"), on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(_("name"), max_length=255)
    client_company = models.CharField(
        _("client company"), max_length=155, null=True, blank=True
    )
    description = models.TextField(_("description"), null=True, blank=True)
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICE, default="To Do"
    )
    priority = models.CharField(
        _("priority"), max_length=20, choices=PRIORITY_CHOICE, default="Low"
    )
    # budget
    total_amount = models.DecimalField(
        _("total amount"), max_digits=5, decimal_places=2, default=0.00
    )
    amount_spent = models.DecimalField(
        _("spent amount"), max_digits=5, decimal_places=2, default=0.00
    )
    estimated_duration = models.IntegerField(
        _("estimated duration"), help_text="estimated duration in days", default=0
    )

    active = models.BooleanField(_("active"), default=False)
    start_date = models.DateField(_("start date"))
    due_date = models.DateField(_("due date"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    update_at = models.DateTimeField(_("update at"), auto_now=True)
    objects = ProjectManager()

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
    
    def get_status_color(self):
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
