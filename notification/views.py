import importlib
from django.shortcuts import render, redirect
from notification.models import Notification

# SHow all notifications
def show_all_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(
        user=user
    ).order_by('-date')

    notification_ids = []
    for notification in notifications:
        notification_ids.append(notification.id)

    context = {
        'user': user,
        'notifications': notifications
    }
    return render(
        request, 
        'notifications/all_notifications.html', 
        context
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
