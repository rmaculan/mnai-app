from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Comment, Likes
from notification.models import Notification
import json

class NotificationTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        
        # Create a test post
        self.post = Post.objects.create(
            title='Test Post',
            subtitle='Test Subtitle',
            content='Test Content',
            author=self.user1,
            status='published'
        )
        
        # Client for API requests
        self.client = Client()
    
    def test_like_notification(self):
        """Test that notifications are managed correctly when a post is liked"""
        self.client.login(username='user2', password='password2')
        
        # Initial count of notifications
        initial_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        ).count()
        
        # Like the post
        response = self.client.post(
            reverse('blog:like_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify like worked
        self.assertEqual(response.status_code, 200)
        
        # Get all notifications after liking
        notifications = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        )
        
        # Verify at least one notification was created
        self.assertTrue(notifications.exists())
        
        # Verify at least one notification has the correct text
        has_correct_text = False
        for notification in notifications:
            if notification.text_preview == "Liked your post":
                has_correct_text = True
                break
        self.assertTrue(has_correct_text, "No notification with 'Liked your post' text found")
        
        # Like the post again - this toggles the like off
        response = self.client.post(
            reverse('blog:like_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify the notifications were removed when unliked
        current_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        ).count()
        self.assertEqual(current_count, 0, "Notifications weren't removed after unliking")
    
    def test_comment_notification(self):
        """Test that a notification is created when a post is commented on"""
        self.client.login(username='user2', password='password2')
        
        # Initial count of notifications
        initial_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=2
        ).count()
        
        # Comment on the post
        response = self.client.post(
            reverse('blog:create_comment', args=[self.post.id]),
            {'comment': 'Test comment'}
        )
        
        # Verify the notification was created
        new_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=2
        ).count()
        self.assertEqual(new_count, initial_count + 1)
    
    def test_dislike_notification(self):
        """Test that a notification is created when a post is disliked"""
        self.client.login(username='user2', password='password2')
        
        # First like the post
        self.client.post(
            reverse('blog:like_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Initial count of notifications
        initial_like_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        ).count()
        initial_dislike_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=5
        ).count()
        
        # Dislike the post
        response = self.client.post(
            reverse('blog:dislike_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify the like notification was removed
        new_like_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        ).count()
        self.assertEqual(new_like_count, 0)
        
        # Verify the dislike notification was created
        new_dislike_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=5
        ).count()
        self.assertEqual(new_dislike_count, initial_dislike_count + 1)
    
    def test_double_like_notification(self):
        """Test that a notification is created when double-liking a post"""
        self.client.login(username='user2', password='password2')
        
        # Initial count of notifications
        initial_count = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        ).count()
        
        # Double-like the post
        response = self.client.post(
            reverse('blog:double_like_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Get all notifications after double-liking
        notifications = Notification.objects.filter(
            user=self.user1, 
            notification_types=1
        )
        
        # Verify at least one notification was created
        self.assertTrue(notifications.exists())
        
        # Verify at least one notification has the correct text
        has_correct_text = False
        for notification in notifications:
            if notification.text_preview == "Double liked your post":
                has_correct_text = True
                break
        self.assertTrue(has_correct_text, "No notification with 'Double liked your post' text found")
