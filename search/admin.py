from django.contrib import admin
from .models import SearchIndex

@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    """
    Admin interface for SearchIndex model.
    """
    list_display = ('title', 'content_type', 'object_id', 'author', 'category', 'date_indexed')
    list_filter = ('content_type', 'category', 'date_indexed')
    search_fields = ('title', 'text_content', 'tags')
    date_hierarchy = 'date_indexed'
    
    readonly_fields = ('date_indexed', 'date_modified')
    
    fieldsets = (
        ('Content Information', {
            'fields': ('title', 'text_content', 'author')
        }),
        ('Classification', {
            'fields': ('content_type', 'object_id', 'tags', 'category')
        }),
        ('Search Optimization', {
            'fields': ('search_vector', 'numeric_field')
        }),
        ('Metadata', {
            'fields': ('url', 'image_url', 'date_indexed', 'date_modified')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize admin listing with select_related"""
        return super().get_queryset(request).select_related('content_type', 'author')
