import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from django.contrib.auth.models import User
import re

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{re.sub(r"[^\w\-.]", "_", self.room_name)}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        
        await self.save_message(sender, message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'receiver': None  # Add this line
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def save_message(self, sender_username, message):
        from marketplace.models import ItemMessage
        
        room = Room.objects.get(room_name=self.room_name)
        sender = User.objects.get(username=sender_username)
        
        # Try to determine receiver from previous messages in this room
        previous_message = Message.objects.filter(
            room=room
            ).exclude(
                sender=sender
                ).order_by('-date').first()
        if previous_message and previous_message.sender:
            receiver = previous_message.sender
        else:
            # If no previous messages from other users, try using room creator
            receiver = room.creator if room.creator.username != sender_username else None
            
            # For item messages, try to find the item seller/buyer relationship
            if 'Item_' in self.room_name:
                try:
                    item_message = ItemMessage.objects.filter(room=room).first()
                    if item_message:
                        if sender == item_message.sender:
                            receiver = item_message.receiver
                        else:
                            receiver = item_message.sender
                except:
                    pass
        
        Message.objects.create(
            room=room, 
            sender=sender, 
            receiver=receiver,
            message=message
        )
