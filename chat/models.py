from django.db import models
from marketplace.models import Item, ItemMessage
from django.contrib.auth.models import User
import datetime


class Room(models.Model):
    room_name = models.CharField(max_length=50)

    def __str__(self):
        return self.room_name

class ItemRoom(Room):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE
        )

    def __str__(self):
        return f"{str(self.item)} - {str(self.room)}"


class Message(models.Model):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE
        )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='sent_messages'
        )
    message = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{str(self.room)} - {self.sender}"

class MarketplaceMessage(ItemMessage):
    item_room = models.ForeignKey(
        ItemRoom, 
        on_delete=models.CASCADE
        )
    market_message = models.TextField()

    
    def __str__(self):
        return f"{str(self.item_room)} - {self.sender}"

