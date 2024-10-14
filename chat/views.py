from django.shortcuts import render, redirect,get_object_or_404
from .models import Room, ItemRoom, Message, MarketplaceMessage
from .consumers import ChatConsumer
from .forms import RoomCreationForm
from django.contrib.auth import login, logout, authenticate
from marketplace.models import Item
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
    item_rooms = ItemRoom.objects.all()
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

        if item_room and request.user.is_authenticated:
            try:
                item_room = ItemRoom.objects.get(
                    item_id=item_id,
                    room=room
                    )
            except ItemRoom.DoesNotExist:
                item_room = None
                print(item_room)
                

        return redirect(
            "room", 
            room_name=room_name, 
            item_room=item_room,
            username=username
            )
    
    context = {
        "rooms": rooms,
        "username": request.user.username,
        "item_rooms": item_rooms
    }
    # print(context)

    return render(request, "chat/index.html", context)

@login_required
def room_view(request, room_name, username):
    existing_room = Room.objects.get(
        room_name__exact=room_name,
        )
    item_room = ItemRoom.objects.all()
    creator = existing_room.creator == request.user.username
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
        "item_room": item_room,
    }
    print(context)
    
    return render(request, "chat/room.html", context)

@login_required
@require_http_methods(["POST"])
def create_room(request):
    if request.method == "POST":
        form = RoomCreationForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data["room_name"]
            creator = request.user
            room = Room.objects.create(
                room_name=room_name,
                creator=creator
                )
            room.save()
            return redirect("chat:room", room_name=room_name, username=creator)
    else:
        form = RoomCreationForm()
    return render(request, "chat/create_room.html", {"form": form})
        

@login_required
def manage_room(request, room_name):
    room = Room.objects.get(
        room_name=room_name,
        item_room=item_room,
        creator=request.user.username,
        )
    messages = Message.objects.filter(
        room=room,
        item_room=item_room,
        )

    if request.user != room.creator:
        return HttpResponseForbidden(
            "You don't have permission to manage this room."
            )
    # Add room management logic here
    context = {
        "room": room,
        "item_room": item_room,
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
        item_room=item_room,
        creator=request.user.username,
    )
    if request.user != room.creator:
        return HttpResponseForbidden(
            "You don't have permission to delete this room."
            )
    else:
        room.delete()
        return redirect("chat:index")

    return render(request, "chat/manage_room.html", context)



