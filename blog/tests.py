from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, BlogMessage
from chat.models import Room, Message
from notification.models import Notification

class MessageTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        
        # Create a test post
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user1,
            content='Test Content',
            status='published'
        )
        
        # Set up test client
        self.client = Client()
    
    def test_post_contact_author(self):
        """Test contacting an author about a specific post"""
        # Login as user2
        self.client.login(username='testuser2', password='password123')
        
        # Submit a message to the post author
        response = self.client.post(
            reverse('blog:contact_author_form', args=[self.post.id]),
            {'message': 'Test message about your post'},
            follow=True
        )
        
        # Check if BlogMessage was created
        self.assertTrue(BlogMessage.objects.filter(sender=self.user2, receiver=self.user1, post=self.post).exists())
        
        # Check if notification was created
        self.assertTrue(Notification.objects.filter(
            sender=self.user2,
            user=self.user1,
            post=self.post,
            notification_types=4  # Message notification type
        ).exists())
        
    def test_direct_message_user(self):
        """Test sending a direct message to a user (not related to a post)"""
        # Login as user1
        self.client.login(username='testuser1', password='password123')
        
        # Submit a direct message to user2
        response = self.client.post(
            reverse('blog:message_user', args=['testuser2']),
            {'message': 'Test direct message'},
            follow=True
        )
        
        # Check if BlogMessage was created with post=None
        self.assertTrue(BlogMessage.objects.filter(
            sender=self.user1, 
            receiver=self.user2,
            post__isnull=True
        ).exists())
        
        # Check if notification was created
        self.assertTrue(Notification.objects.filter(
            sender=self.user1,
            user=self.user2,
            post__isnull=True,
            notification_types=4  # Message notification type
        ).exists())
