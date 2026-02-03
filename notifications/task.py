from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from notifications.models import Notification
from projects.models import Project
from tasks.models import Task

User = get_user_model()


@shared_task
def create_notification(actor_name, verb, object_id):
    try:
        actor = User.objects.get(username=actor_name)
        content_type = ContentType.objects.get_for_model(Project)

        project = Project.objects.get(id=object_id)
        members = project.team.member.exclude(id=project.owner.id)
        for recipient in members:
            notification = Notification.objects.create(
                actor=actor,
                recipient=recipient,
                content_type=content_type,
                content_object=project,
                verb=verb,
            )
        return notification.verb
    except User.DoesNotExist:
        return None
    except ContentType.DoesNotExist:
        return None


@shared_task
def create_task_notification(actor_name, verb, object_id):
    try:
        actor = User.objects.get(username=actor_name)
        content_type = ContentType.objects.get_for_model(Task)

        task = Task.objects.get(id=object_id)
        members = task.team.member.exclude(id=task.owner.id)
        for recipient in members:
            notification = Notification.objects.create(
                actor=actor,
                recipient=recipient,
                content_type=content_type,
                content_object=task,
                verb=verb,
            )
        return notification.verb
    except User.DoesNotExist:
        return None
    except ContentType.DoesNotExist:
        return None


@shared_task
def notify_team_due_project_task():
    projects_soon = Project.objects.due_t_or_less()
    for pro in projects_soon:
        verb = f"Reminder the {pro.name} is due soon"
        actor = pro.owner.username
        members = pro.team.member.exclude(id=pro.owner.id)
        for member in members:
            create_notification.delay(actor_name=actor, verb=verb, object_id=pro.id)
