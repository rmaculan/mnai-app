from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Post, Tag
from marketplace.models import Item, CategoryModel
from search.models import SearchIndex
from search.services import SearchService

class Command(BaseCommand):
    help = 'Populate the search index with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting search index population...'))
        
        # Clear existing index
        SearchIndex.objects.all().delete()
        self.stdout.write('Cleared existing search index')

        # Create test users if they don't exist
        self.stdout.write('Creating test users...')
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
            self.stdout.write(f"Created user: {user1.username}")
        else:
            self.stdout.write(f"User already exists: {user1.username}")
            
        user2, created = User.objects.get_or_create(
            username='testuser2',
            defaults={
                'email': 'test2@example.com'
            }
        )
        if created:
            user2.set_password('testpassword2')
            user2.save()
            self.stdout.write(f"Created user: {user2.username}")
        else:
            self.stdout.write(f"User already exists: {user2.username}")
        
        # Create test tags
        self.stdout.write('Creating test tags...')
        tag1, created = Tag.objects.get_or_create(
            name='Technology',
            defaults={'slug': 'technology'}
        )
        if created:
            self.stdout.write(f"Created tag: {tag1.name}")
        else:
            self.stdout.write(f"Tag already exists: {tag1.name}")
            
        tag2, created = Tag.objects.get_or_create(
            name='Health',
            defaults={'slug': 'health'}
        )
        if created:
            self.stdout.write(f"Created tag: {tag2.name}")
        else:
            self.stdout.write(f"Tag already exists: {tag2.name}")
        
        # Create test blog posts
        self.stdout.write('Creating test blog posts...')
        try:
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
                self.stdout.write(f"Created post: {post1.title}")
            else:
                self.stdout.write(f"Post already exists: {post1.title}")
                
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
                self.stdout.write(f"Created post: {post2.title}")
            else:
                self.stdout.write(f"Post already exists: {post2.title}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating blog posts: {str(e)}"))
        
        # Create test categories
        self.stdout.write('Creating test categories...')
        category1, created = CategoryModel.objects.get_or_create(
            name='Electronics',
            defaults={'slug': 'electronics'}
        )
        if created:
            self.stdout.write(f"Created category: {category1.name}")
        else:
            self.stdout.write(f"Category already exists: {category1.name}")
            
        category2, created = CategoryModel.objects.get_or_create(
            name='Clothing',
            defaults={'slug': 'clothing'}
        )
        if created:
            self.stdout.write(f"Created category: {category2.name}")
        else:
            self.stdout.write(f"Category already exists: {category2.name}")
        
        # Create test marketplace items
        self.stdout.write('Creating test marketplace items...')
        try:
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
                self.stdout.write(f"Created item: {item1.name}")
            else:
                self.stdout.write(f"Item already exists: {item1.name}")
                
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
                self.stdout.write(f"Created item: {item2.name}")
            else:
                self.stdout.write(f"Item already exists: {item2.name}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating marketplace items: {str(e)}"))
        
        # Reindex all content
        self.stdout.write('Indexing test data for search...')
        try:
            SearchService.reindex_all()
            index_count = SearchIndex.objects.count()
            self.stdout.write(self.style.SUCCESS(f"Successfully indexed {index_count} items"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error indexing data: {str(e)}"))
            
        self.stdout.write(self.style.SUCCESS('Search index population completed successfully!'))
