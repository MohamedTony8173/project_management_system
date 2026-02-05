from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class CommentManager(models.Manager):
    def filter_by_instance_model(self,instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return self.filter(content_type=content_type,object_id=instance.pk)

class Comment(models.Model):

    user = models.ForeignKey(
        User, verbose_name="user", on_delete=models.CASCADE, related_name="comments"
    )
    content_type = models.ForeignKey(
        ContentType, verbose_name=_("content type"), on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    
    comment_body = models.TextField(_("comment"))
    created_at = models.DateTimeField(_("created at "), auto_now_add=True)
    objects = CommentManager()

    def __str__(self):
        return f"Comment By - {self.user.username} - {self.content_object}"

    class Meta:
        ordering = ("-created_at",)

    def date_created_format(self):
        return self.created_at.strftime("%d %b %I-%M %p")
