from .models import Notification

def notification_unread(request):
    if request.user.is_authenticated:
        # TODO TOMORROW notification count
        notifications_count = Notification.objects.unread_notification(request.user).count()
        notifications_un = Notification.objects.unread_notification(request.user)[:4]
    else:
        notifications_count = 0
    return {
        'notifications_un':notifications_un,
        'notifications_count':notifications_count
    }
    
    

        