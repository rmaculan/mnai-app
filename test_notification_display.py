"""
Test script to diagnose notification display issues.
Run this script using:
python manage.py shell < test_notification_display.py
"""

from notification.models import Notification
from django.contrib.auth.models import User
from django.db import connection

print("===== NOTIFICATION DISPLAY TEST =====")

# 1. Check for duplicate records in database
print("\n----- DATABASE RECORDS CHECK -----")
all_notifications = Notification.objects.all().order_by('-date')
print(f"Total notifications: {all_notifications.count()}")

# Check notifications by user
users = User.objects.all()
for user in users:
    notifications = Notification.objects.filter(user=user)
    if notifications.exists():
        print(f"\nUser: {user.username} - {notifications.count()} notifications")
        
        # Check for duplicate like notifications
        like_notifications = notifications.filter(notification_types=1)
        if like_notifications.exists():
            print(f"  Like notifications: {like_notifications.count()}")
            # Group by sender and post
            by_sender_post = {}
            for notification in like_notifications:
                key = (notification.sender_id, notification.post_id)
                if key not in by_sender_post:
                    by_sender_post[key] = []
                by_sender_post[key].append(notification)
            
            for key, duplicates in by_sender_post.items():
                if len(duplicates) > 1:
                    print(f"  DUPLICATE LIKES: {len(duplicates)} notifications from sender_id={key[0]} on post_id={key[1]}")
                    for i, n in enumerate(duplicates):
                        print(f"    Notification {i+1}: ID={n.id}, Date={n.date}")
        
        # Check for duplicate comment notifications
        comment_notifications = notifications.filter(notification_types=2)
        if comment_notifications.exists():
            print(f"  Comment notifications: {comment_notifications.count()}")
            # Group by sender and post
            by_sender_post = {}
            for notification in comment_notifications:
                key = (notification.sender_id, notification.post_id)
                if key not in by_sender_post:
                    by_sender_post[key] = []
                by_sender_post[key].append(notification)
            
            for key, duplicates in by_sender_post.items():
                if len(duplicates) > 1:
                    print(f"  DUPLICATE COMMENTS: {len(duplicates)} notifications from sender_id={key[0]} on post_id={key[1]}")
                    for i, n in enumerate(duplicates):
                        print(f"    Notification {i+1}: ID={n.id}, Date={n.date}")

# 2. Check the template for potential duplicate loops
print("\n----- TEMPLATE CHECK -----")
# Check all_notifications.html for multiple loops
from django.template.loader import get_template
try:
    template = get_template('notifications/all_notifications.html')
    template_content = template.template.source
    print(f"Template length: {len(template_content)} characters")
    
    # Count for loops through notifications
    for_loop_count = template_content.count("{% for notification in notifications %}")
    print(f"Number of notification for loops: {for_loop_count}")
    
    # Check if notifications is used in multiple places
    notification_var_refs = template_content.count("{{ notification")
    notifications_var_refs = template_content.count("{{ notifications")
    print(f"References to notification (singular): {notification_var_refs}")
    print(f"References to notifications (plural): {notifications_var_refs}")
except Exception as e:
    print(f"Error checking template: {e}")

# 3. Check for multiple context sources
print("\n----- CONTEXT PROCESSORS CHECK -----")
# Examine if notifications appear in multiple context sources
from django.conf import settings

context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
notification_processors = [cp for cp in context_processors if 'notif' in cp]
print(f"Notification-related context processors: {notification_processors}")

# 4. Check view implementations for duplicate data
print("\n----- VIEWS CHECK -----")
from notification.views import show_all_notifications
import inspect

view_source = inspect.getsource(show_all_notifications)
print(f"show_all_notifications view source:")
print(view_source)

# Check the SQL queries that would run for a notification page
print("\n----- SQL QUERIES CHECK -----")
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM notification_notification")
    row = cursor.fetchone()
    print(f"Total notifications (direct SQL): {row[0]}")

# Execute raw SQL to find duplicates
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT sender_id, user_id, post_id, notification_types, COUNT(*) as count
        FROM notification_notification
        GROUP BY sender_id, user_id, post_id, notification_types
        HAVING COUNT(*) > 1
    """)
    rows = cursor.fetchall()
    if rows:
        print("DUPLICATE NOTIFICATIONS FOUND:")
        for row in rows:
            print(f"  sender_id={row[0]}, user_id={row[1]}, post_id={row[2]}, type={row[3]}, count={row[4]}")
    else:
        print("No duplicate notifications found in database based on sender, user, post, and type.")

print("\n===== TEST COMPLETE =====")
