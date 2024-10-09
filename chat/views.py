from .models import Chat, ItemMessage
from blog.models import Profile
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from typing import AsyncGenerator
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
        'item_user',
        'sender', 
        'receiver'
        )

    combined_data = []

    for chat in chats:
        if chat['chat_user']:
            combined_data.append({
            'id': chat.id,
            'user': chat['chat_user'].username,
            'sender': chat.sender.username,
            'receiver': chat.receiver.username,
            'content': chat.content,
            'is_read': chat.is_read,
            'timestamp': chat.created_at.isoformat(),
            'related_item': chat.item_message.item.name 
            
            if chat.item_message

            else None
            }) 
        else:
            continue
        

    for item_message in item_messages:
        if item_message['item_user']:
            combined_data.append({
                'id': item_message.id,
                'user': item_message['item_user'].username,
                'sender': item_message.sender.username,
                'receiver': item_message.receiver.username,
                'content': item_message.message,
                'is_read': False,
                'timestamp': item_message.timestamp,
                'related_item': item_message.item.name

                if item_message.item

                else None
            })
        else:
            continue

    return combined_data

@login_required
def index(request):
    user = request.user
    chats = Chat.get_chat(user=request.user)
    item_chats = ItemMessage.get_messages(user=user)
    active_chat = None
    instant_messages = None
    item_messages = None
    profile = get_object_or_404(Profile, user=user)

    if chats:
        chat = chats[0]
        item_chat = item_chats[0]
        active_chat = chat['chat_user'].username
        instant_messages = Chat.objects.filter(
            chat_user=user, receiver=chat['chat_user']
        ).order_by('-created_at')
        item_messages = ItemMessage.objects.filter(
            item_user=user, receiver=chat['item_user']
        ).order_by('-timestamp')
        
        # Fetch combined chats data
        combined_chats_data = combined_chats(request)
        
        # Process combined chats data
        processed_combined_chats = combined_chats_data
        
        for chat in chats:
            if chat['chat_user'].username == active_chat:
                combined_chats_data = combined_chats(request)

        for item_chat in item_chats:
            if item_chat['item_user'].username == active_chat:
                combined_chats_data = combined_chats(request)

        all_messages = []

        for message in item_messages:
            all_messages.append({
                'id': message.id,
                'user': message.item_user.username,
                'sender': message.sender.username,
                'receiver': message.receiver.username,
                'content': message.message,
                'is_read': False,
                'timestamp': message.timestamp,
                'related_item': message.item.name

                if message.item

                else None
            })

        for message in instant_messages:
            all_messages.append({
                'id': message.id,
                'user': message.chat_user.username,
                'sender': message.sender.username,
                'receiver': message.receiver.username,
                'content': message.content,
                'is_read': message.is_read,
                'timestamp': message.created_at,
                'related_item': False

                if 'related_item' == message.item_message

                else None
            })
        
        all_messages.extend(processed_combined_chats)

    else:
        context = {'profile': profile}

    context = {
        'instant_messages': instant_messages,
        'item_messages': item_messages,
        'chats': chats,
        'item_chats': item_chats,
        'active_chat': active_chat,
        'profile': profile
    }
    print(f"Chats: {active_chat}")
    return render(request, 'chat/instant_messages.html', context)

def get_instant_messages(request, username):
    
    user = request.user
    chats = Chat.get_chat(user=user)
    item_chats = ItemMessage.get_messages(user=user)
    active_chat = username
    instant_messages = Chat.objects.filter(
        chat_user=user, 
        receiver__username=username
        )
    instant_messages.update(is_read=True)
    item_messages = ItemMessage.objects.filter(
        Q(item_user=user) | 
        Q(receiver__username=username)
        )
    
    print(f"Active chat username: {username}")
    try:
        active_chat = User.objects.get(username=username)
        print(f"Found active_direct: {active_chat.username}")
    except User.DoesNotExist:
        print(f"No user found with username: {username}")
        return HttpResponse("Invalid chat", status=400)
    
    # if not username:
    #     username = user.username
    
    for chat in chats:
        if chat['chat_user'] == username:
            chat['unread'] = 0

    for item_chat in item_chats:
        if item_chat['item_user'] == username:
            item_chat['unread'] = 0

    try:
        active_chat = User.objects.get(username=active_chat)
    except User.DoesNotExist:
        return HttpResponse("Invalid chat", status=400)

    context = {
        'instant_messages': instant_messages,
        'item_messages': item_messages,
        'active_chat': active_chat,
    }
    return render(request, 'chat/instant_messages.html', context)

def send_message(request):
    from_user = request.user
    to_user_input = request.POST.get('to_user')
    content = request.POST.get('content')

    if request.method == 'POST':
        if not content:
            return HttpResponse("Message content is required", status=400)

        try:
            to_user = User.objects.get(username=to_user_input)
        except User.DoesNotExist:
            return HttpResponse(f"Invalid user: {to_user_input}", status=400)

        Chat.sender_chat(from_user, to_user, content)
        return redirect('message')

def search_users(request):
    query = request.GET.get('q')
    context = {}
    if query:
        users = User.objects.filter(username__icontains=query)

        paginator = Paginator(users, 10)
        page = request.GET.get('page')
        users_pagination = paginator.get_page(page)

        context = {
            'users': users_pagination
            }
    return render(request, 'chat/search.html', context)

def new_conversation(request, username):
    from_user = request.user
    content = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception:
        return redirect('search')
    if from_user != to_user:
        Chat.sender_chat(from_user, to_user, content)
    return redirect('message')
