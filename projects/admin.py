from django.contrib import admin
from .models import Project
from notifications.task import create_notification


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "owner",
        "name",
        "client_company",
        "description",
        "status",
        "priority",
        "start_date",
        "due_date",
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
            verb = f"Project {obj.name} Assigned!"
        else:
            verb = f"Project {obj.name} Updated!"
        super().save_model(request, obj, form, change)
        # send notification
        actor = request.user.username
        obj_id = obj.id

        create_notification.delay(actor_name=actor, verb=verb, object_id=obj_id)


admin.site.register(Project,ProjectAdmin)
