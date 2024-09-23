from .models import Chat, ItemMessage
from blog.models import Profile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from typing import AsyncGenerator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, StreamingHttpResponse, HttpResponse
import random
import json

@login_required
def combined_chats(request):
    chats = Chat.objects.all().select_related(
        'chat_user', 
        'sender', 
        'receiver'
        )
    item_messages = ItemMessage.objects.all().select_related(
        'sender', 
        'receiver'
        )

    combined_data = []

    for chat in chats:
        combined_data.append({
            'id': chat.id,
            'user': chat.chat_user.username,
            'sender': chat.sender.username,
            'receiver': chat.receiver.username,
            'content': chat.content,
            'is_read': chat.is_read,
            'timestamp': chat.created_at.isoformat(),
            'related_item': chat.item_message.item.name if chat.item_message else None
        })

    for item_message in item_messages:
        combined_data.append({
            'id': item_message.id,
            'user': item_message.sender.username,
            'sender': item_message.sender.username,
            'receiver': item_message.receiver.username,
            'content': item_message.message,
            'is_read': False,
            'timestamp': item_message.timestamp.isoformat(),
            'related_item': item_message.item.name if item_message.item else None
        })

    return combined_data

@login_required
def inbox(request):
    chats = Chat.get_chat(user=request.user)
    profile = get_object_or_404(Profile, user=request.user)

    if chats:
        chat = chats[0]
        active_chat = chat['chat_user']
        instant_messages = Chat.objects.filter(
            Q(chat_user=request.user) | 
            Q(receiver__pk=chat['receiver']),
            is_read=False
        ).order_by('-created_at')
        
        # Fetch combined chats data
        combined_chats_data = combined_chats(request)
        
        # Process combined chats data
        processed_combined_chats = combined_chats_data
        
        # Update unread counts
        for chat in chats:
            if chat['chat_user'] == active_chat:
                combined_chats_data = combined_chats(request)

        all_messages = []
        
        # Process combined chats data
        processed_combined_chats = combined_chats_data
        for message in instant_messages:
            all_messages.append({
                'id': message.id,
                'user': message.chat_user.username,
                'sender': message.sender.username,
                'receiver': message.receiver.username,
                'content': message.content,
                'is_read': message.is_read,
                'timestamp': message.created_at,
                'related_item': None
            })
        
        all_messages.extend(processed_combined_chats)

    else:
        context = {'profile': profile}

    context = {
        'instant_messages': all_messages,
        'active_chat': active_chat,
        'profile': profile
    }
    print(context)
    return render(request, 'chat/inbox.html', context)

def get_instant_messages(request, username):
    user = request.user
    chats = Chat.get_chat(user=user)
    active_chat = username
    instant_messages = Chat.objects.filter(
        chat_user=user, 
        receiver__username=username
        )
    instant_messages.update(is_read=True)


    for chat in chats:
        if chat['chat_user'] == username:
            chat['unread'] = 0

    context = {
        'chat': chat,
        'active_chat': active_chat,
        'instant_messages': instant_messages

    }
    return render(request, 'chat/instant_messages.html', context)

