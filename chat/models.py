from django.db import models
from marketplace.models import Item, ItemMessage
from blog.models import Profile
from django.contrib.auth.models import User
import datetime


class Room(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='creator_id',
        default=None,
        )
    room_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.room_name

class ItemRoom(Room):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE,
        related_name='item_id',
        default=False,
        null=True
        )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seller_id',
        default=False,
        null=True
        )

    def __str__(self):
        return f"{str(self.item)} - {str(self.room_name)}"

class RegularRoom(Room):
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,
        related_name='profile_id'
        )

class Message(models.Model):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE
        )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='sender_id',
        )
    message = models.TextField()
    date = models.DateTimeField(
        default=datetime.datetime.now)

    def __str__(self):
        return f"{str(self.room)} - {self.sender}"

class MarketplaceMessage(ItemMessage):
    item_room = models.ForeignKey(
        ItemRoom, 
        on_delete=models.CASCADE,
        related_name='item_room_id',
        )
    market_message = models.TextField()
    date = models.DateTimeField(
        default=datetime.datetime.now)
        
    def __str__(self):
        return f"{str(self.item_room)} - {self.sender}"

