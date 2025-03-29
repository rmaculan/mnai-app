from django.core.management.base import BaseCommand
from notification.models import Notification
from collections import defaultdict
import sys

class Command(BaseCommand):
    help = 'Find and remove duplicate notifications in the database'

    def handle(self, *args, **options):
        # Print to stderr for debugging
        print("Starting deduplication of notifications...", file=sys.stderr)
        
        # Get all notifications
        all_notifications = Notification.objects.all()
        total_count = all_notifications.count()
        print(f"Total notifications: {total_count}", file=sys.stderr)
        self.stdout.write(f"Total notifications: {total_count}")
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("No notifications found in the database."))
            return
        
        # Group notifications by key attributes to find duplicates
        notification_groups = defaultdict(list)
        
        for notification in all_notifications:
            # Create a tuple of attributes that should make a notification unique
            key = (
                notification.sender_id,
                notification.user_id,
                notification.post_id,
                notification.notification_types,
                # Don't include date since duplicates may have different timestamps
            )
            notification_groups[key].append(notification)
        
        # Find groups with more than one notification (duplicates)
        duplicate_count = 0
        deleted_count = 0
        
        for key, notifications in notification_groups.items():
            if len(notifications) > 1:
                duplicate_count += 1
                self.stdout.write(f"Found {len(notifications)} duplicates for notification: "
                                 f"Sender: {notifications[0].sender}, "
                                 f"User: {notifications[0].user}, "
                                 f"Post: {notifications[0].post_id}, "
                                 f"Type: {notifications[0].notification_types}")
                
                # Keep the oldest notification and delete the rest
                notifications.sort(key=lambda x: x.date)  # Sort by date
                kept = notifications[0]
                
                for duplicate in notifications[1:]:
                    self.stdout.write(f"  Deleting duplicate ID: {duplicate.id} from {duplicate.date}")
                    duplicate.delete()
                    deleted_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Found {duplicate_count} groups of duplicates. "
            f"Deleted {deleted_count} duplicate notifications."
        ))
