from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator

from blog.models import Post, Tag
from marketplace.models import Item, CategoryModel
from .services import SearchService
from .models import SearchIndex

@require_GET
def search_view(request):
    """
    Main search view that accepts various search parameters and returns results.
    Demonstrates both hash table and binary search approaches.
    """
    # Get search parameters
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'hybrid')  # hybrid, hash, binary
    content_filter = request.GET.get('content', 'all')  # all, blog, marketplace
    category = request.GET.get('category', None)
    tag = request.GET.get('tag', None)
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    sort_by = request.GET.get('sort', 'date_indexed')  # date_indexed, title, etc.
    
    # Initialize variables
    search_results = []
    content_type_obj = None
    
    # Set content type filter
    if content_filter == 'blog':
        content_type_obj = ContentType.objects.get_for_model(Post)
    elif content_filter == 'marketplace':
        content_type_obj = ContentType.objects.get_for_model(Item)
    
    # Process tags and categories
    tags = [tag] if tag else None
    
    # Convert price values to float if provided
    min_value = float(min_price) if min_price and min_price.isdigit() else None
    max_value = float(max_price) if max_price and max_price.isdigit() else None
    
    # Perform search based on selected method
    if search_type == 'hash':
        # Use hash table search for exact matches
        search_results = SearchService.hash_table_search(
            term=query, 
            tags=tags, 
            category=category
        )
    elif search_type == 'binary':
        # Use binary search for numeric fields
        search_results = SearchService.binary_search(
            field='numeric_field',
            min_value=min_value,
            max_value=max_value
        )
        # Additional filter for text if query provided
        if query:
            search_results = search_results.filter(
                Q(title__icontains=query) | Q(text_content__icontains=query)
            )
    else:
        # Default to hybrid search
        search_results = SearchService.hybrid_search(
            term=query,
            tags=tags,
            category=category,
            min_value=min_value,
            max_value=max_value,
            content_type=content_type_obj
        )
    
    # Apply sorting
    search_results = search_results.order_by(sort_by)
    
    # Organize results into categories
    categorized_results = {
        'blog': [],
        'marketplace': []
    }
    
    # Group results by content type
    blog_type = ContentType.objects.get_for_model(Post)
    marketplace_type = ContentType.objects.get_for_model(Item)
    
    for result in search_results:
        if result.content_type == blog_type:
            categorized_results['blog'].append(result)
        elif result.content_type == marketplace_type:
            categorized_results['marketplace'].append(result)
    
    # Get all available categories for filtering
    blog_tags = Tag.objects.all()
    marketplace_categories = CategoryModel.objects.all()
    
    # Paginate results
    paginator = Paginator(search_results, 10)  # 10 results per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'search_type': search_type,
        'content_filter': content_filter,
        'page_obj': page_obj,
        'categorized_results': categorized_results,
        'blog_tags': blog_tags,
        'marketplace_categories': marketplace_categories,
        'search_count': search_results.count(),
        'category': category,
        'tag': tag,
        'min_price': min_price,
        'max_price': max_price
    }
    
    return render(request, 'search/search_results.html', context)

def reindex_search(request):
    """Admin view to manually trigger reindexing"""
    if request.user.is_staff:
        SearchService.reindex_all()
        # Redirect back to the referring page
        return render(request, 'search/reindex_complete.html', {
            'count': SearchIndex.objects.count()
        })
    else:
        # Handle unauthorized access
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to perform this action.")

def search_icon_view(request):
    """View for the search icon implementation"""
    return render(request, 'search/search_icon.html')
