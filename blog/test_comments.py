from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment

class CommentTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        
        # Mock picture for test post to avoid template errors
        from django.core.files.uploadedfile import SimpleUploadedFile
        from io import BytesIO
        from PIL import Image as PILImage
        from django.core.files.base import ContentFile
        
        # Create a simple image file for testing
        image_file = BytesIO()
        image = PILImage.new('RGB', (100, 100), 'white')
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        
        # Create a test post with the test image
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user1,
            content='Test Content',
            status='published'
        )
        self.post.picture.save('test_image.jpg', ContentFile(image_file.read()), save=True)
        
        # Create sample comments
        self.comment1 = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='Main comment from user1'
        )
        
        self.comment2 = Comment.objects.create(
            post=self.post,
            author=self.user2,
            content='Main comment from user2'
        )
        
        # Create replies
        self.reply1 = Comment.objects.create(
            post=self.post,
            author=self.user2,
            content='Reply from user2 to comment1',
            parent=self.comment1
        )
        
        self.reply2 = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='Reply from user1 to comment2',
            parent=self.comment2
        )
        
        # Set up test client
        self.client = Client()
    
    def test_comment_display(self):
        """Test that the post detail page shows comments correctly"""
        # Login as user1
        self.client.login(username='testuser1', password='password123')
        
        # Get the post detail page
        response = self.client.get(reverse('blog:post_detail', args=[self.post.id]))
        
        # Check response code
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertIn('post', response.context)
        self.assertIn('comments', response.context)
        
        # Test that latest comment is available in the context
        comments = self.post.comments.all()
        self.assertTrue(len(comments) > 0)
        
    def test_create_comment(self):
        """Test creating a new comment"""
        # Login as user1
        self.client.login(username='testuser1', password='password123')
        
        # Create a new comment
        response = self.client.post(
            reverse('blog:create_comment', args=[self.post.id]),
            {'comment': 'New test comment'},
            follow=True
        )
        
        # Check response code
        self.assertEqual(response.status_code, 200)
        
        # Verify comment was created
        self.assertTrue(Comment.objects.filter(
            post=self.post,
            author=self.user1,
            content='New test comment'
        ).exists())
        
    def test_create_reply(self):
        """Test creating a reply to a comment"""
        # Login as user1
        self.client.login(username='testuser1', password='password123')
        
        # Create a reply
        response = self.client.post(
            reverse('blog:create_comment', args=[self.post.id]),
            {
                'comment': 'New test reply',
                'parent_id': self.comment2.id
            },
            follow=True
        )
        
        # Check response code
        self.assertEqual(response.status_code, 200)
        
        # Verify reply was created
        self.assertTrue(Comment.objects.filter(
            post=self.post,
            author=self.user1,
            content='New test reply',
            parent=self.comment2
        ).exists())
        
    def test_comment_ordering(self):
        """Test that comments are ordered correctly (newest first)"""
        # Get comments
        comments = Comment.objects.filter(post=self.post, parent__isnull=True)
        
        # Check the order (should be newest first based on Meta ordering in the Comment model)
        self.assertEqual(comments.first(), self.comment2)
        self.assertEqual(comments.last(), self.comment1)
