from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Tag
from marketplace.models import Item, CategoryModel
from .models import SearchIndex
from .services import SearchService
import json

class SearchIndexTest(TestCase):
    """
    Test case for the SearchIndex model and related search functionality.
    """
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpassword1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword2'
        )
        
        # Create blog post test data
        self.tag1 = Tag.objects.create(name='Technology', slug='technology')
        self.tag2 = Tag.objects.create(name='Health', slug='health')
        
        self.post1 = Post.objects.create(
            title='Test Post on Technology',
            subtitle='A technology review',
            content='This is a test post about the latest technology trends.',
            author=self.user1,
            status='published',
            tags=self.tag1,
            slug='test-post-tech'
        )
        
        self.post2 = Post.objects.create(
            title='Health and Wellness',
            subtitle='Tips for staying healthy',
            content='This post covers health topics and wellness advice.',
            author=self.user2,
            status='published',
            tags=self.tag2,
            slug='health-wellness'
        )
        
        # Create marketplace item test data
        self.category1 = CategoryModel.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.category2 = CategoryModel.objects.create(
            name='Clothing',
            slug='clothing'
        )
        
        self.item1 = Item.objects.create(
            name='Laptop Computer',
            description='High-performance laptop for professionals.',
            price=999.99,
            quantity=5,
            seller=self.user1,
            category=self.category1
        )
        
        self.item2 = Item.objects.create(
            name='Designer T-shirt',
            description='Comfortable cotton t-shirt with modern design.',
            price=29.99,
            quantity=20,
            seller=self.user2,
            category=self.category2
        )
        
        # Index test data
        SearchService.reindex_all()
    
    def test_search_index_creation(self):
        """Test that SearchIndex records are created correctly"""
        # Check post indexing
        self.assertEqual(SearchIndex.objects.count(), 4)  # 2 posts + 2 items
        
        # Check specific indexes
        post_indices = SearchIndex.objects.filter(title__icontains='Technology').count()
        self.assertEqual(post_indices, 1)
        
        item_indices = SearchIndex.objects.filter(title__icontains='Laptop').count()
        self.assertEqual(item_indices, 1)
    
    def test_hash_table_search(self):
        """Test hash table search functionality"""
        # Search by tag
        results = SearchService.hash_table_search(tags=['Technology'])
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Test Post on Technology')
        
        # Search by category
        results = SearchService.hash_table_search(category='Clothing')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Designer T-shirt')
    
    def test_binary_search(self):
        """Test binary search functionality"""
        # Search by price range
        results = SearchService.binary_search('numeric_field', 20, 100)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Designer T-shirt')
        
        # Search by higher price range
        results = SearchService.binary_search('numeric_field', 500, 1500)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Laptop Computer')
    
    def test_hybrid_search(self):
        """Test hybrid search functionality"""
        # Text search
        results = SearchService.hybrid_search(term='laptop')
        self.assertEqual(results.count(), 1)
        
        # Multi-criteria search
        results = SearchService.hybrid_search(
            author=self.user1,
            min_value=900,
            max_value=1100
        )
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Laptop Computer')
    
    def test_search_view(self):
        """Test the search view functionality"""
        client = Client()
        
        # Test basic search
        response = client.get(reverse('search:search_view') + '?q=technology')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post on Technology')
        
        # Test category filter
        response = client.get(reverse('search:search_view') + '?category=Electronics')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop Computer')
        
        # Test price range
        response = client.get(reverse('search:search_view') + '?min_price=900&max_price=1000')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop Computer')
        
        # Test combined filters
        response = client.get(reverse('search:search_view') + '?q=design&content=marketplace')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Designer T-shirt')

class SearchManualTest:
    """
    Utility class for manually testing search functionality.
    Not a TestCase - used for manual debugging and verification.
    """
    @staticmethod
    def run_tests():
        """Run manual tests and print results"""
        # Clear existing index
        SearchIndex.objects.all().delete()
        print(f"Current index count: {SearchIndex.objects.count()}")
        
        # Index all content
        SearchService.reindex_all()
        print(f"After indexing, count: {SearchIndex.objects.count()}")
        
        # Query tests
        print("\nRunning search tests:")
        
        # Test basic term search
        results = SearchService.hybrid_search(term='technology')
        print(f"Search for 'technology': {results.count()} results")
        for result in results:
            print(f" - {result.title} ({result.content_type.model})")
        
        # Test category search
        results = SearchService.hybrid_search(category='Electronics')
        print(f"\nSearch for category 'Electronics': {results.count()} results")
        for result in results:
            print(f" - {result.title} ({result.content_type.model})")
        
        # Test price range
        results = SearchService.hybrid_search(min_value=500, max_value=1500)
        print(f"\nSearch for price 500-1500: {results.count()} results")
        for result in results:
            print(f" - {result.title} ({result.numeric_field})")
        
        # Test author search
        try:
            author = User.objects.first()
            if author:
                results = SearchService.hybrid_search(author=author)
                print(f"\nSearch for author '{author.username}': {results.count()} results")
                for result in results:
                    print(f" - {result.title} ({result.content_type.model})")
        except Exception as e:
            print(f"Author search failed: {str(e)}")
        
        print("\nSearch testing complete")
        return True
