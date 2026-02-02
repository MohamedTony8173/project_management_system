from .models import Notification

def notification_unread(request):
    if request.user.is_authenticated:
        # TODO TOMORROW notification count
        notifications = Notification.objects.unread_notification(request.user)[:5]
    else:
        notifications = 0  
    return {
        'notifications':notifications
    }