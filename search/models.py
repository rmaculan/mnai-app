from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVectorField
from django.contrib.auth.models import User

class SearchIndex(models.Model):
    """
    A unified search index for all searchable content in the application.
    Uses both hash table approach (tags) and binary search friendly fields (date_indexed).
    """
    # Content type machinery for generic relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)  # UUID compatible
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Main searchable text content
    title = models.CharField(max_length=255)
    text_content = models.TextField()
    
    # Hash table compatible fields for exact matching
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.JSONField(default=list, help_text="List of tags for hash table lookup")
    category = models.CharField(max_length=100, null=True, blank=True)
    
    # Binary search friendly fields
    date_indexed = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    numeric_field = models.FloatField(null=True, blank=True, help_text="For binary search on numeric values")
    
    # For full-text search optimization
    search_vector = SearchVectorField(null=True, blank=True)
    
    # Additional metadata
    url = models.CharField(max_length=500, blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['date_indexed']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.content_type.model})"
    
    def get_tags_hash(self):
        """
        Creates a hash table (dictionary) of tags for O(1) lookup.
        """
        return {tag: True for tag in self.tags}
    
    @staticmethod
    def binary_search(queryset, field_name, target_value):
        """
        Implements binary search for sorted querysets.
        Note: This is for demonstration as Django's ORM already optimizes queries.
        """
        items = list(queryset.order_by(field_name).values_list('id', field_name))
        left, right = 0, len(items) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if items[mid][1] == target_value:
                return queryset.filter(id=items[mid][0])
            elif items[mid][1] < target_value:
                left = mid + 1
            else:
                right = mid - 1
                
        return queryset.none()  # Return empty if not found
