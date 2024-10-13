from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Room, Message, User
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = f"""
        room_{
            self.scope['url_route']['kwargs'].get('room_name', 'item_id')
            }
            """
        self.room_group_name = f"{self.room_name}_group"

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
        logger.info(f"Received message: {text_data}")
        
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender_id']
        room_name = text_data_json['room_name']
        item_room = text_data_json['item_room_id']

        logger.info(
            f"""
            Message details: message={message}, 
            sender={sender}, room_name={room_name}
            """)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender.id,
                'room_name': room_name,
            })

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender_id']
        room_name = event['room_name']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender.id,
            'room_name': room_name,
            'item_room_id': item_room
        }))

    async def send_message(self, event):
        data = event["message"]
        try:
            new_message = await self.create_message(data)
            response = {
                "sender_id": new_message.sender.username, 
                "message": new_message.message
                }
            await self.send(text_data=json.dumps(
                {"message": response}))
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            await self.send(text_data=json.dumps({
                'message': 'Error: Unable to send message',
                'type': 'chat_message',
                }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def create_message(self, data):
        sender = self.get_user(data["sender_id"])
        get_room = Room.objects.get(room_name=data["room_name"])

        if not Message.objects.filter(
            message=data["message"], 
            sender=data["sender_id"]
        ).exists():
            new_message = Message.objects.create(
                room=get_room, 
                message=data["message"], 
                sender=data["sender_id"]
            )


# region:old_code

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import Room, Message


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
#         await self.channel_layer.group_add(self.room_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, code):
#         await self.channel_layer.group_discard(self.room_name, self.channel_name)
#         self.close(code)

#     async def receive(self, text_data):
#         # print("Recieved Data")
#         data_json = json.loads(text_data)
#         # print(data_json)

#         event = {"type": "send_message", "message": data_json}

#         await self.channel_layer.group_send(self.room_name, event)

#     async def send_message(self, event):
#         data = event["message"]
#         await self.create_message(data=data)

#         response = {"sender": data["sender"], "message": data["message"]}

#         await self.send(text_data=json.dumps({"message": response}))

#     @database_sync_to_async
#     def create_message(self, data):
#         get_room = Room.objects.get(room_name=data["room_name"])

#         if not Message.objects.filter(
#             message=data["message"], sender=data["sender"]
#         ).exists():
#             new_message = Message.objects.create(
#                 room=get_room, message=data["message"], sender=data["sender"]


# endregion             )