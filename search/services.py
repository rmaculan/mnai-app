from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from collections import defaultdict
from blog.models import Post, Tag
from marketplace.models import Item, CategoryModel
from .models import SearchIndex

class SearchService:
    """
    Service class for handling search operations across blog posts and marketplace items.
    Implements both hash table and binary search approaches.
    """
    
    @staticmethod
    def index_post(post):
        """Index a blog post for searching"""
        content_type = ContentType.objects.get_for_model(Post)
        
        # Get or create the search index
        search_index, created = SearchIndex.objects.get_or_create(
            content_type=content_type,
            object_id=str(post.id)
        )
        
        # Update the search index with post data
        search_index.title = post.title
        search_index.text_content = f"{post.subtitle} {post.caption} {post.content}"
        search_index.author = post.author
        
        # Extract tags
        tags = []
        if post.tags:
            tags.append(post.tags.name)
        
        search_index.tags = tags
        search_index.url = f"/blog/post/{post.id}/"
        
        # Add image URL if available, otherwise use default
        if post.picture and hasattr(post.picture, 'url'):
            search_index.image_url = post.picture.url
        else:
            search_index.image_url = '/media/default.jpg'
            
        # Add numeric field for verification score
        search_index.numeric_field = post.verification_score
        
        search_index.save()
        return search_index
    
    @staticmethod
    def index_item(item):
        """Index a marketplace item for searching"""
        content_type = ContentType.objects.get_for_model(Item)
        
        # Get or create the search index
        search_index, created = SearchIndex.objects.get_or_create(
            content_type=content_type,
            object_id=str(item.id)
        )
        
        # Update the search index with item data
        search_index.title = item.name
        search_index.text_content = item.description
        search_index.author = item.seller
        
        # Extract category as tag
        tags = []
        if item.category:
            tags.append(item.category.name)
            search_index.category = item.category.name
        
        search_index.tags = tags
        search_index.url = f"/marketplace/item/{item.id}/"
        
        # Add image URL if available, otherwise use default
        if item.image and hasattr(item.image, 'url'):
            search_index.image_url = item.image.url
        else:
            search_index.image_url = '/media/defaults/default_item.jpg'
            
        # Add numeric field for price (useful for range searches)
        search_index.numeric_field = float(item.price)
        
        search_index.save()
        return search_index
    
    @staticmethod
    def reindex_all():
        """Reindex all searchable content"""
        # Clear existing index
        SearchIndex.objects.all().delete()
        
        # Index all posts
        for post in Post.objects.filter(status='published'):
            SearchService.index_post(post)
            
        # Index all items
        for item in Item.objects.all():
            SearchService.index_item(item)
    
    @staticmethod
    def hash_table_search(term=None, tags=None, category=None):
        """
        Perform search using hash table approach for exact matches.
        Good for tag/category searching.
        """
        # Create empty result set
        results = set()
        
        # Create a hash table (dictionary) for O(1) lookups
        if tags:
            # Convert tags to a set for O(1) containment checks
            tag_set = set(tags)
            
            # Get all search indices
            indices = SearchIndex.objects.all()
            
            # Iterate through indices and check tags using hash lookups
            for index in indices:
                # Convert index tags to set for intersection operation
                index_tags = set(index.tags)
                
                # If any tag matches (intersection not empty)
                if index_tags.intersection(tag_set):
                    results.add(index.id)
        
        # Add category search
        if category:
            category_indices = SearchIndex.objects.filter(category=category)
            for index in category_indices:
                results.add(index.id)
        
        # Add term search
        if term:
            term_indices = SearchIndex.objects.filter(
                Q(title__icontains=term) | 
                Q(text_content__icontains=term)
            )
            for index in term_indices:
                results.add(index.id)
        
        # Return queryset of matching indices
        return SearchIndex.objects.filter(id__in=results)
    
    @staticmethod
    def binary_search(field, min_value=None, max_value=None):
        """
        Perform binary search on sorted numeric fields.
        Good for price range or date range searching.
        """
        queryset = SearchIndex.objects.all()
        
        # Sort the queryset by the field
        queryset = queryset.order_by(field)
        
        # Apply min value if provided
        if min_value is not None:
            queryset = queryset.filter(**{f"{field}__gte": min_value})
            
        # Apply max value if provided
        if max_value is not None:
            queryset = queryset.filter(**{f"{field}__lte": max_value})
        
        return queryset
    
    @staticmethod
    def hybrid_search(term=None, author=None, tags=None, category=None, 
                      min_value=None, max_value=None, content_type=None):
        """
        Hybrid search combining hash table and binary search approaches.
        """
        # Start with all indices
        queryset = SearchIndex.objects.all()
        
        # Filter by content type if specified
        if content_type:
            content_type_obj = ContentType.objects.get_for_model(content_type)
            queryset = queryset.filter(content_type=content_type_obj)
        
        # Apply text search term
        if term:
            queryset = queryset.filter(
                Q(title__icontains=term) | 
                Q(text_content__icontains=term)
            )
        
        # Apply author filter
        if author:
            queryset = queryset.filter(author=author)
            
        # Apply tag filter using hash table concept
        if tags:
            tag_q = Q()
            for tag in tags:
                # This emulates a hash lookup by creating OR conditions
                tag_q |= Q(tags__contains=[tag])
            queryset = queryset.filter(tag_q)
            
        # Apply category filter
        if category:
            queryset = queryset.filter(category=category)
            
        # Apply numeric range filters (binary search concept)
        if min_value is not None:
            queryset = queryset.filter(numeric_field__gte=min_value)
            
        if max_value is not None:
            queryset = queryset.filter(numeric_field__lte=max_value)
            
        return queryset
