#!/usr/bin/env python
"""
Script to add test data to the search index and run test searches.
This can be run manually to populate the search index with sample data
and verify search functionality.
"""
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Post, Tag
from marketplace.models import Item, CategoryModel
from search.models import SearchIndex
from search.services import SearchService

def add_test_data():
    """Add test data for search functionality testing"""
    print("Adding test users...")
    # Create test users if they don't exist
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'test1@example.com',
            'is_staff': True
        }
    )
    if created:
        user1.set_password('testpassword1')
        user1.save()
        print(f"Created user: {user1.username}")
    else:
        print(f"User already exists: {user1.username}")
        
    user2, created = User.objects.get_or_create(
        username='testuser2',
        defaults={
            'email': 'test2@example.com'
        }
    )
    if created:
        user2.set_password('testpassword2')
        user2.save()
        print(f"Created user: {user2.username}")
    else:
        print(f"User already exists: {user2.username}")
    
    print("\nAdding test tags...")
    # Create test tags
    tag1, created = Tag.objects.get_or_create(
        name='Technology',
        defaults={'slug': 'technology'}
    )
    if created:
        print(f"Created tag: {tag1.name}")
    else:
        print(f"Tag already exists: {tag1.name}")
        
    tag2, created = Tag.objects.get_or_create(
        name='Health',
        defaults={'slug': 'health'}
    )
    if created:
        print(f"Created tag: {tag2.name}")
    else:
        print(f"Tag already exists: {tag2.name}")
    
    print("\nAdding test blog posts...")
    # Create test blog posts
    post1, created = Post.objects.get_or_create(
        title='Test Post on Technology',
        defaults={
            'subtitle': 'A technology review',
            'content': 'This is a test post about the latest technology trends.',
            'author': user1,
            'status': 'published',
            'tags': tag1,
            'slug': 'test-post-tech'
        }
    )
    if created:
        print(f"Created post: {post1.title}")
    else:
        print(f"Post already exists: {post1.title}")
        
    post2, created = Post.objects.get_or_create(
        title='Health and Wellness',
        defaults={
            'subtitle': 'Tips for staying healthy',
            'content': 'This post covers health topics and wellness advice.',
            'author': user2,
            'status': 'published',
            'tags': tag2,
            'slug': 'health-wellness'
        }
    )
    if created:
        print(f"Created post: {post2.title}")
    else:
        print(f"Post already exists: {post2.title}")
    
    print("\nAdding test categories...")
    # Create test categories
    category1, created = CategoryModel.objects.get_or_create(
        name='Electronics',
        defaults={'slug': 'electronics'}
    )
    if created:
        print(f"Created category: {category1.name}")
    else:
        print(f"Category already exists: {category1.name}")
        
    category2, created = CategoryModel.objects.get_or_create(
        name='Clothing',
        defaults={'slug': 'clothing'}
    )
    if created:
        print(f"Created category: {category2.name}")
    else:
        print(f"Category already exists: {category2.name}")
    
    print("\nAdding test marketplace items...")
    # Create test marketplace items
    item1, created = Item.objects.get_or_create(
        name='Laptop Computer',
        defaults={
            'description': 'High-performance laptop for professionals.',
            'price': 999.99,
            'quantity': 5,
            'seller': user1,
            'category': category1
        }
    )
    if created:
        print(f"Created item: {item1.name}")
    else:
        print(f"Item already exists: {item1.name}")
        
    item2, created = Item.objects.get_or_create(
        name='Designer T-shirt',
        defaults={
            'description': 'Comfortable cotton t-shirt with modern design.',
            'price': 29.99,
            'quantity': 20,
            'seller': user2,
            'category': category2
        }
    )
    if created:
        print(f"Created item: {item2.name}")
    else:
        print(f"Item already exists: {item2.name}")
    
    print("\nIndexing data for search...")
    # Reindex all content
    SearchIndex.objects.all().delete()
    SearchService.reindex_all()
    print(f"Indexed {SearchIndex.objects.count()} items")
    
    return True

def run_test_searches():
    """Run a series of test searches to verify functionality"""
    print("\n===== RUNNING TEST SEARCHES =====")
    
    print("\n1. Search by term:")
    results = SearchService.hybrid_search(term='technology')
    print(f"Results for 'technology': {results.count()}")
    for result in results:
        print(f" - {result.title} ({result.content_type.model})")
    
    print("\n2. Search by category:")
    results = SearchService.hybrid_search(category='Electronics')
    print(f"Results for category 'Electronics': {results.count()}")
    for result in results:
        print(f" - {result.title} ({result.content_type.model})")
    
    print("\n3. Search by price range:")
    results = SearchService.hybrid_search(min_value=500, max_value=1500)
    print(f"Results for price range 500-1500: {results.count()}")
    for result in results:
        print(f" - {result.title} (${result.numeric_field})")
    
    print("\n4. Search by author:")
    try:
        user = User.objects.get(username='testuser1')
        results = SearchService.hybrid_search(author=user)
        print(f"Results for author '{user.username}': {results.count()}")
        for result in results:
            print(f" - {result.title} ({result.content_type.model})")
    except User.DoesNotExist:
        print("User testuser1 does not exist")
    
    print("\n5. Hash table search for tags:")
    results = SearchService.hash_table_search(tags=['Technology'])
    print(f"Hash table results for tag 'Technology': {results.count()}")
    for result in results:
        print(f" - {result.title}")
    
    print("\n6. Binary search for numeric field:")
    results = SearchService.binary_search('numeric_field', min_value=20, max_value=50)
    print(f"Binary search results for range 20-50: {results.count()}")
    for result in results:
        print(f" - {result.title} (value: {result.numeric_field})")
    
    print("\n===== TEST SEARCHES COMPLETED =====")

if __name__ == "__main__":
    print("Starting test data creation and search tests...")
    add_test_data()
    run_test_searches()
    print("\nScript completed successfully!")
