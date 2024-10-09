import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Max, Q


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
    item_user = models.ForeignKey(
        User,
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

    @classmethod
    def get_messages(cls, user):
        item_users = []
        messages = cls.objects.filter(
            Q(item_user=user) | Q(receiver=user)
        ).values('receiver').annotate(
            last=Max('timestamp')
        ).order_by('-last')
        for message in messages:
            receiver_id = message['receiver']
            receiver = User.objects.get(pk=receiver_id)
            item_users.append({
                'item_user': receiver.username,
                'last': message['last'],
                'unread': cls.objects.filter(
                    item_user=user,
                    receiver__pk=receiver_id
                ).count(),
                'receiver': receiver_id
            })
        return item_users
    
    def sender_message(from_user, to_user, message):
        sender_message = ItemMessage(
            item_user=from_user,
            sender=from_user,
            receiver=to_user,
            message=message
            )
        sender_message.save()
        
        receiver_message = ItemMessage(
            item_user=to_user,
            sender=from_user,
            receiver=to_user,
            message=message
            )
        receiver_message.save()
        return sender_message
    
class Order(models.Model):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField() 
    buyer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.item.name} - {self.buyer}"

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

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"

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



    

