from django.shortcuts import get_object_or_404, render, redirect
from marketplace.models import Item  # Remove duplicate import
from .models import Room, Message
from .consumers import ChatConsumer
from .forms import RoomCreationForm
from django.contrib.auth import login, logout, authenticate
from marketplace.models import Item
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.http import HttpResponseForbidden
import json
import logging

logger = logging.getLogger(__name__)
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:index') 
    else:
        form = UserCreationForm()
    return render(
        request, 'chat/register.html', {'form': form}
        )

def login_view(request):
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('chat:index')
        else:
            form = AuthenticationForm()
        return render(
            request, 'chat/login.html', {'form': form}
            )

def logout_view(request):
    logger.info("Logout view accessed")
    logout(request)

    return redirect('chat:index')

@login_required
def index(request):
    rooms = Room.objects.all()
    # item_rooms = ItemRoom.objects.all().order_by("-created_at")
    if request.method == "POST":
        room_name = request.POST["room"]
        
        try:
            existing_room = Room.objects.get(
                room_name__exact=room_name
                )
            # print(existing_room)
        except Room.DoesNotExist:
            existing_room = None

        if existing_room:
            return redirect(
                "room", 
                room_name=room_name, 
                username=request.user.username
                )

            return redirect(
                "room", 
                room_name=room_name, 
                username=request.user.username  # Fix undefined variable
            )
    
    context = {
        "rooms": rooms,
        "username": request.user.username,
    }
    # print(context)

    return render(request, "chat/index.html", context)

@login_required
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(email__icontains=query)
    ).exclude(id=request.user.id)

    context = {
        'users': users,
        'query': query,
    }

    return render(request, 'chat/search_users.html', context)

@login_required
def inbox(request):
    user = request.user
    receivers = User.objects.filter(
        Q(sender_id__sender=user) | 
        Q(receiver_id__receiver=user)
    ).distinct()
    rooms = Room.objects.filter(
        creator=user,
        participants__in=receivers
        ).order_by("-created_at")

    context = {
        "user": request.user,
        "receivers": receivers,
        "rooms": rooms,  
    }

    return render(request, "chat/inbox.html", context)

@login_required
@require_http_methods(["GET", "POST"])
def create_room(request):
    if request.method == "POST":
        form = RoomCreationForm(request.POST)
        if form.is_valid():
            item_id = request.POST.get('item_id')
            user_id = request.POST.get('user_id')
    
            if item_id:
                item = get_object_or_404(Item, id=item_id)
                seller = item.seller
                room_name = f"{item.name} - {item.seller.username}"
            elif user_id:
                receiver = get_object_or_404(User, id=user_id)
                room_name = f"Chat with {receiver.username}"
            else:
                room_name = request.POST.get('room_name')

            room = Room.objects.create(
                creator=request.user,
                room_name=room_name,
            )
            room.save()
            return redirect('chat:room', room_name=room_name)
    else:
        form = RoomCreationForm()
        user_id = request.GET.get('user_id')
        if user_id:
            receiver = get_object_or_404(User, id=user_id)
            form.fields['room_name'].initial = f"Chat with {receiver.username}"

    return render(request, "chat/create_room.html", {"form": form})
 
@login_required
def room_view(request, room_name):
    existing_room = Room.objects.get(
        room_name__exact=room_name,
        )
    creator = existing_room.creator == request.user  # Define creator variable
    current_user = request.user
    messages = Message.objects.filter(
        room=existing_room
        )
    # print(messages)

    filtered_messages = messages.filter(
        sender=current_user
        )
    # print(filtered_messages)
    
    context = {
        "creator": creator,
        "messages": messages,
        "room_name": existing_room,
    }
    logger.debug(f"Room context: {context}")
    
    return render(request, "chat/room.html", context)

@login_required
def manage_room(request, room_name):
    room = Room.objects.get(
        room_name=room_name,
        creator=request.user.username,
        )
    messages = Message.objects.filter(
        room=room,
        )

    if request.user != room.creator:
        return HttpResponseForbidden(
            "You don't have permission to manage this room."
            )
    context = {
        "room": room,
        "creator": creator,
        "messages": messages,
    }
    return render(request, "chat/manage_room.html", context)

# delete room
@login_required
@require_http_methods(["POST"])
def delete_room(request, room_name):
    room = Room.objects.get(
        room_name=room_name,
        creator=request.user,  # Fix to use request.user
    )
    if request.user != room.creator:
        return HttpResponseForbidden(
            "You don't have permission to delete this room."
            )
    else:
        room.delete()
        return redirect("chat:index")

    return render(request, "chat/manage_room.html", context)

# search users
