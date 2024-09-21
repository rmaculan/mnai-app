from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from marketplace.models import UserMessage

class Chat(models.Model):
    chat_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="chat_user"
        )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="from_user"
        )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="to_user"
        )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def sender_chat(from_user, to_user, content):
        sender_chat = Chat(
            user=from_user,
            sender = from_user,
            receiver = to_user,
            content = content,
            is_read = True
            )
        sender_chat.save()
    
        recipient_chat = Chat(
            user=to_user,
            sender = from_user,
            receiver = from_user,
            content = content,
            is_read = True
            )
        recipient_chat.save()
        return sender_chat

    def get_chat(user):
        users = []
        chats = Chat.objects.filter(
            chat_user=user).values('receiver').annotate(
                last=Max('created_at')).order_by('-last')
        for chat in chats:
            users.append({
                'chat_user': User.objects.get(
                    pk=chat['receiver']),
                'last': chat['last'],
                'unread': Chat.objects.filter(
                    chat_user=user, 
                    receiver__pk=chat['receiver'], 
                    is_read=False
                    ).count()
            })
        return users




