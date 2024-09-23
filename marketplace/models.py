import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class MarketplaceProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE
        )
    profile_image = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True
        )
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)

class CategoryModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
        )
    image = models.ImageField(
        upload_to='items/', 
        blank=True, 
        null=True
        )
    date_listed = models.DateTimeField(default=datetime.datetime.now)
    is_sold = models.BooleanField(default=False)
    if is_sold:
        date_sold = models.DateTimeField(
            default=datetime.datetime.now
            )
    condition = models.CharField(
        max_length=20, 
        choices=[
            ('N', 'New'), 
            ('U', 'Used')
            ],
        default='U'
                                  )
    category = models.ForeignKey(
        CategoryModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        )

    def __str__(self):
        return self.name
    
class ItemMessage(models.Model):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE, 
        null=True
        )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
        )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
        )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username}"
    
class Conversation(models.Model):
    participants = models.ManyToManyField(
        User, 
        related_name='conversations'
        )
    messages = models.ManyToManyField(
        ItemMessage,
        related_name='conversation'
        )
    start_time = models.DateTimeField(auto_now_add=True)
    

class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField() 
    buyer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.item.name} - {self.buyer}"

class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  
    comment = models.TextField()
    reviewer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.item.name} - {self.reviewer}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"

class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bought_transactions'
        )
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sold_transactions'
        )

    def __str__(self):
        return f"{self.order.item.name} - {self.buyer.username} - {self.seller.username}"

class PostModel(models.Model):
    STATUS_CHOICES = (
        ('D', 'Draft'),
        ('P', 'Published'),
        ('A', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=1, 
        choices=STATUS_CHOICES, 
        default='D'
        )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        'CategoryModel', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        )

    def __str__(self):
        return self.title

class CommentModel(models.Model):
    post = models.ForeignKey(
        PostModel, 
        related_name='comments', 
        on_delete=models.CASCADE
        )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

class LikeModel(models.Model):
    post = models.ForeignKey(
        PostModel, 
        related_name='likes', 
        on_delete=models.CASCADE
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')  # Prevents duplicate likes from the same user

    def __str__(self):
        return f"Like by {self.user} on {self.post.title}"
    

