from django.urls import path
from notification.views import show_all_notifications, delete_notification

app_name = 'notification'

urlpatterns = [
    path('', show_all_notifications, name='show-all-notifications'),
    path('<noti_id>/delete', delete_notification, name='delete-notification'),


]
