from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class NotificationManager(models.Manager):
    def get_user_notification(self, user):
        return self.filter(recipient=user)

    def unread_notification(self, user):
        return self.get_user_notification(user).filter(read=False)

    def read_notification(self, user):
        return self.get_user_notification(user).filter(read=True)


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        verbose_name="recipient",
        on_delete=models.CASCADE,
        related_name="notification",
    )
    actor = models.ForeignKey(
        User, verbose_name="actor", on_delete=models.CASCADE, related_name="action"
    )
    verb = models.CharField(_("verb"), max_length=250)
    content_type = models.ForeignKey(
        ContentType, verbose_name=_("content type"), on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(_("created at "))
    read = models.BooleanField(_("read"), default=False)
    objects = NotificationManager()

    def __str__(self):
        return f"{self.actor} - {self.verb} - {self.content_object}"

    class Meta:
        ordering = ("-created_at",)

    def date_created_format(self):
        return self.created_at.strftime("%d %b %I-%M %p")
