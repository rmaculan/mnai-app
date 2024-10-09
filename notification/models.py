from django.db import models
from django.contrib.auth.models import User
# from post.models import Post

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, 'Like'), 
        (2, 'Comment'), 
        (3, 'Follow')
        )

    post = models.ForeignKey(
            "blog.Post", 
            on_delete=models.CASCADE, 
            related_name="post_notification", 
            null=True
            )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="sender_notification" 
        )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="user_notification" 
        )
    notification_types = models.IntegerField(
        choices=NOTIFICATION_TYPES, 
        null=True, 
        blank=True
        )
    text_preview = models.CharField(
        max_length=100, 
        blank=True
        )
    date = models.DateTimeField(
        auto_now_add=True
        )
    is_seen = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.text_preview



