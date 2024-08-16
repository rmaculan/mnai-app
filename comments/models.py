from django.contrib.auth import get_user_model

from django.conf import settings
from django.db import models
from django.utils import timezone

User = get_user_model()


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        db_index=True,
        null=True,
        blank=True,
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments", db_index=True
    )

    class Meta:
        ordering = ["created_at"]

    def is_root_comment(self):
        """Check if this comment is a root comment (no parent)"""
        return self.parent is None

    def get_children(self):
        """Retrieve all direct child comments."""
        return Comment.objects.filter(parent=self)

