import os
import shutil
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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

    def all_upcoming_active(self):
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

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"pk": self.pk})
    
    def get_kanban_url(self):
        return reverse("projects:kanban_dashboard", kwargs={"pk": self.pk})


def attach_file_location(instance, fileName):
    date_upload = timezone.now().strftime("%Y-%m-%d")
    return f"attach/{instance.project.name}/{ date_upload}/ {fileName}"


class AttachMentFile(models.Model):
    project = models.ForeignKey(
        Project,
        verbose_name=_("project"),
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="user_attachments",
    )
    name = models.CharField(_("name"), max_length=150)
    file_upload = models.FileField(_("file name"), upload_to=attach_file_location)
    uploaded_at = models.DateTimeField(_("upload at"), auto_now_add=True)

    def __str__(self):
        return self.name


# this for delete also image if he was deleted
@receiver(post_delete, sender=AttachMentFile)
def delete_file_on_delete(sender, instance, **kwargs):
    if instance.file_upload:
        # if i remove just a path of file_upload
        # if os.path.isfile(instance.file_upload.path):
        #     os.remove(instance.file_upload.path)

        # this for delete folder that has folder  hold photo path like /username/2026-01-30
        folder_path = os.path.dirname(os.path.dirname(instance.file_upload.path))
        # Deletes the folder and the image
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
