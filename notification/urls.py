from django.urls import path
from notification.views import show_all_notifications, show_notification, delete_notification

urlpatterns = [
    path('', show_all_notifications, name='show-all-notifications'),
    path('<noti_id>/', show_notification, name='show-notification'),
    path('<noti_id>/delete', delete_notification, name='delete-notification'),


]
