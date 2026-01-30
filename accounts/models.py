from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
import os
from django.utils.timesince import timesince
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra):
        extra.setdefault("is_active", True)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)

        return self.create_user(email, username, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email"), max_length=255, unique=True, db_index=True)
    username = models.CharField(_("username"), max_length=60, unique=True)
    is_active = models.BooleanField(_("active"), default=False)
    is_staff = models.BooleanField(_("staff"), default=False)
    is_superuser = models.BooleanField(_("superuser"), default=False)

    join_at = models.DateTimeField(_("join at"), auto_now_add=True)
    last_login = models.DateTimeField(_("last login"), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="profile"
    )
    photo = models.ImageField(_("photo"), upload_to="user_profile/")
    phone = models.CharField(_("phone"), max_length=16, null=True, blank=True)
    address = models.CharField(_("address"), max_length=255, null=True, blank=True)
    update_at = models.DateTimeField(_("update"), auto_now=True)
    bio = models.CharField(_("bio"), max_length=255, null=True, blank=True)
    location = models.CharField(_("location"), max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def get_profile_image(self):
        try:
            image = self.photo.url
        except:
            image = os.path.join("media/default_user.jpg")
        return image
    
    @property
    def get_date_joined(self):
        time_difference = timezone.now() - self.user.join_at
        if time_difference <= timezone.timedelta(days=2):
            return timesince(self.user.join_at) + " ago"
        else:
            return self.user.join_at.strftime('%d %b')


# Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, **kwargs):
    # if there a user it will updated . else it created one
    Profile.objects.get_or_create(user=instance)
