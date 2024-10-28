import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Max, Q
# from chat.models import Message


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
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2
        )
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
    date_listed = models.DateTimeField(
        default=datetime.datetime.now
        )
    is_sold = models.BooleanField(default=False)
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

    @property
    def is_sold(self):
        return self.is_sold
    
class ItemMessage(models.Model):
    room = models.ForeignKey(
        'chat.Room', 
        on_delete=models.CASCADE,
        default=None
        )
    item_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='item_user',
        null=True,
        blank=True
        )
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE, 
        null=True
        )
    sender= models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='item_messages_sent',
        default=None
        )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='receiver'
        )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
class Order(models.Model):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField() 
    buyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='bought_orders'
    )


class Review(models.Model):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE
        )
    rating = models.PositiveIntegerField()  
    comment = models.TextField()
    reviewer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.item.name} - {self.reviewer}"

class Cart(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
        )
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()  

class Transaction(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE
        )
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



    

