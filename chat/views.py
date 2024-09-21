from .models import Chat
from django.contrib.auth.models import User
from blog.models import Profile
from django.db.models import Q
from datetime import datetime
import asyncio
from django.contrib.auth.decorators import login_required
from typing import AsyncGenerator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, StreamingHttpResponse, HttpResponse
import random

@login_required
def inbox(request):
    user = request.user
    chats = Chat.get_chat(user=request.user)
    profile = get_object_or_404(Profile, user=user)
    active_chat = None
    instant_messages = None

    if chats:
        chat = chats[0]
        active_chat = chat['chat_user'].username
        instant_messages = Chat.objects.filter(
            Q(chat_user=user) | Q(receiver__pk=chat['receiver']),
            is_read=False
        ).order_by('-created_at')

        for chat in chats:
            if chat['chat_user'].username == active_chat:
                chat['unread'] = 0

    context = {
        'instant_messages': instant_messages,
        'chats': chats,
        'active_chat': active_chat,
        'profile': profile
    }
    return render(request, 'chat/instant_messages.html', context)

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
        if chat['chat_user'].username == username:
            chat['unread'] = 0

    context = {
        'chat': chat,
        'active_chat': active_chat,
        'instant_messages': instant_messages

    }
    return render(request, 'chat/instant_messages.html', context)

