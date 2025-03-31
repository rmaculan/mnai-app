from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField

class Tag(models.Model):
    """Tag for categorizing conversations"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6c757d')  # Bootstrap secondary color
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Conversation(models.Model):
    """Represents a complete conversation session"""
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('deepseek', 'DeepSeek'),
        ('claude', 'Claude'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(
        max_length=50, 
        choices=PROVIDER_CHOICES, 
        default='openai'
    )
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    shared_with = models.ManyToManyField(
        User, 
        related_name='shared_conversations',
        blank=True
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.title}'

    class Meta:
        ordering = ['-updated_at']

class Chat(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_function_call = models.BooleanField(default=False)
    function_name = models.CharField(max_length=100, blank=True, null=True)
    function_args = models.JSONField(blank=True, null=True)
    function_result = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'

    class Meta:
        ordering = ['created_at']
