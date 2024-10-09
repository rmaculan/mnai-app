from django.db import models
from django.db.models import Q
from django.db.models import Max
from django.contrib.auth.models import User
from marketplace.models import ItemMessage




# region: old code

# class Chat(models.Model):
#     chat_user = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name="chat_user"
#         )
#     sender = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name="from_user"
#         )
#     receiver = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name="to_user"
#         )
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     item_message = models.ForeignKey(
#         ItemMessage, 
#         on_delete=models.CASCADE, 
#         null=True,
#         default=None,
#         related_name="item_message"
#         )
    
#     @classmethod
#     def get_chat(cls, user):
#         users = []
#         chats = cls.objects.filter(
#             Q(chat_user=user) | Q(receiver=user)
#         ).values('receiver').annotate(
#             last=Max('created_at')
#         ).order_by('-last')
#         for chat in chats:
#             receiver_id = chat['receiver']
#             receiver = User.objects.get(pk=receiver_id)
#             users.append({
#                 'chat_user': receiver.username,
#                 'last': chat['last'],
#                 'unread': cls.objects.filter(
#                     chat_user=user,
#                     receiver__pk=receiver_id,
#                     is_read=False
#                 ).count(),
#                 'receiver': receiver_id
#             })
#             return users

#     @classmethod
#     def sender_chat(cls, from_user, to_user, content):
#         if not content:
#             raise ValueError("Message content is required")

#         sender_chat = cls(
#             chat_user=from_user,
#             sender=from_user,
#             receiver=to_user,
#             content=content,
#             is_read=False
#         )
#         sender_chat.save()

#         recipient_chat = cls(
#             chat_user=to_user,
#             sender=from_user,
#             receiver=from_user,
#             content=content,
#             is_read=False
#         )
#         recipient_chat.save()
#         return sender_chat

# endregion
    
        




