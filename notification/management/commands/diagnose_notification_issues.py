from django.core.management.base import BaseCommand
from notification.models import Notification
from django.contrib.auth.models import User
from blog.models import Post, Comment, Likes
import sys

class Command(BaseCommand):
    help = 'Diagnose notification-related issues'

    def handle(self, *args, **options):
        self.stdout.write("======== NOTIFICATION DIAGNOSTIC TOOL ========")
        
        # 1. Check total notifications
        total_notifications = Notification.objects.count()
        self.stdout.write(f"Total notifications in database: {total_notifications}")
        
        # 2. Check notifications by type
        likes_notifications = Notification.objects.filter(notification_types=1).count()
        comment_notifications = Notification.objects.filter(notification_types=2).count()
        follow_notifications = Notification.objects.filter(notification_types=3).count()
        
        self.stdout.write(f"Likes notifications: {likes_notifications}")
        self.stdout.write(f"Comment notifications: {comment_notifications}")
        self.stdout.write(f"Follow notifications: {follow_notifications}")
        
        # 3. Check if there are users with excessive notifications
        users = User.objects.all()
        for user in users:
            notification_count = Notification.objects.filter(user=user).count()
            if notification_count > 0:
                self.stdout.write(f"User '{user.username}' has {notification_count} notifications")
                
                # Check if this user has duplicate notifications
                likes_to_check = {}
                comments_to_check = {}
                
                for notification in Notification.objects.filter(user=user):
                    if notification.notification_types == 1 and notification.post_id:  # Like
                        key = (notification.sender_id, notification.post_id)
                        if key in likes_to_check:
                            likes_to_check[key] += 1
                        else:
                            likes_to_check[key] = 1
                    
                    elif notification.notification_types == 2 and notification.post_id:  # Comment
                        key = (notification.sender_id, notification.post_id)
                        if key in comments_to_check:
                            comments_to_check[key] += 1
                        else:
                            comments_to_check[key] = 1
                
                # Report duplicates
                for (sender_id, post_id), count in likes_to_check.items():
                    if count > 1:
                        sender = User.objects.get(id=sender_id)
                        post = Post.objects.get(id=post_id)
                        self.stdout.write(f"  DUPLICATE: {count} like notifications from {sender.username} on post '{post.title}'")
                
                for (sender_id, post_id), count in comments_to_check.items():
                    if count > 1:
                        sender = User.objects.get(id=sender_id)
                        post = Post.objects.get(id=post_id)
                        self.stdout.write(f"  DUPLICATE: {count} comment notifications from {sender.username} on post '{post.title}'")
        
        # 4. Print out individual notifications for inspection
        self.stdout.write("\nIndividual notifications (sample of up to 10):")
        sample_notifications = Notification.objects.all().order_by('-date')[:10]
        for i, notification in enumerate(sample_notifications):
            self.stdout.write(f"\n--- Notification {i+1} ---")
            self.stdout.write(f"ID: {notification.id}")
            self.stdout.write(f"Type: {notification.notification_types}")
            self.stdout.write(f"Sender: {notification.sender.username}")
            self.stdout.write(f"User: {notification.user.username}")
            if notification.post:
                self.stdout.write(f"Post: {notification.post.title}")
            self.stdout.write(f"Date: {notification.date}")
            self.stdout.write(f"Is seen: {notification.is_seen}")
        
        self.stdout.write("\nDiagnostic complete!")
