import importlib
from django.shortcuts import render, redirect
from notification.models import Notification

# Show all notifications
def show_all_notifications(request):
    # The notifications are already added to the context by our context processor
    # So we don't need to retrieve them again here
    return render(
        request, 
        'notifications/notifications_clean.html'
        )
    
def show_notification(request):
    user = request.user
    notification = Notification.objects.filter(user=user).order_by('-date')

    context = {
        'user': user,
        'notification': notification,

    }
    return render(
        request, 
        'notifications/notification.html', 
        context
        )

def delete_notification(request, noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('notification:show-all-notifications')
