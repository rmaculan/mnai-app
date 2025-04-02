from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=50, default="openai")  # Required field in DB
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - {self.user.username}'
    
    def get_first_message(self):
        """Return the first message of the conversation for preview purposes"""
        first_message = self.messages.order_by('created_at').first()
        if first_message:
            return first_message.message[:50] + '...' if len(first_message.message) > 50 else first_message.message
        return "Empty conversation"
    
    class Meta:
        ordering = ['-updated_at']

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Additional fields from the database
    is_function_call = models.BooleanField(default=False)  # Required field in DB
    function_name = models.CharField(max_length=100, null=True, blank=True)
    function_args = models.JSONField(null=True, blank=True)
    function_result = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username}: {self.message}'
    
    class Meta:
        ordering = ['created_at']
