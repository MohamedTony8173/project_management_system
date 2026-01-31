from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Team(models.Model):
    name = models.CharField(_("name"), max_length=50)
    description = models.TextField(_("description"))
    team_leader = models.ForeignKey(User, verbose_name=_("team_leader"), on_delete=models.CASCADE,related_name='team_leader')
    member = models.ManyToManyField(User, verbose_name=_("member"),related_name='teams')
    created_by = models.ForeignKey(User, verbose_name=_("created by"), on_delete=models.CASCADE,related_name='created_team')
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def __str__(self):
        return self.name
    