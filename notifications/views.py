from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from .models import Notification


class NotificationListView(ListView):
    def get_queryset(self):
        super().get_queryset()
        notifications = Notification.objects.get_user_notification(self.request.user)
        return notifications

    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 12


class MakeReadNotificationsView(View):
    def get(self, request, notification_id):
        user = request.user
        notification = get_object_or_404(
            Notification, id=notification_id, recipient=user
        )
        return render(request, "notifications/notification_list.html")

    def post(self, request, notification_id):
        user = request.user
        notification = get_object_or_404(
            Notification, id=notification_id, recipient=user
        )
        notification.read = True
        notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



