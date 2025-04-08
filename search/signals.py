from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from blog.models import Post
from marketplace.models import Item
from .services import SearchService

@receiver(post_save, sender=Post)
def index_post_on_save(sender, instance, created, **kwargs):
    """
    Signal handler to automatically index blog posts when they are created or updated.
    Only published posts are indexed.
    """
    # Only index published posts
    if instance.status == 'published':
        SearchService.index_post(instance)

@receiver(post_save, sender=Item)
def index_item_on_save(sender, instance, created, **kwargs):
    """
    Signal handler to automatically index marketplace items when they are created or updated.
    """
    SearchService.index_item(instance)

# Additional signal handlers could be added for:
# - Removing items from search index on deletion
# - Handling changes to tags or categories
