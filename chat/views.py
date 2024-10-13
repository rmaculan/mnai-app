from django.shortcuts import render, redirect
from .models import Room, ItemRoom, Message, MarketplaceMessage
from .consumers import ChatConsumer
from marketplace.models import Item
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
import json
import logging

logger = logging.getLogger(__name__)
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index') 
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
                return redirect('blog:index')
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
    if request.method == "POST":
        username = request.POST["username"]
        seller = request.POST["seller"]
        room_name = request.POST["room"]
        item_room = request.POST["room"]
        
        try:
            existing_room = Room.objects.get(
                room_name__exact=room_name)
        except Room.DoesNotExist:
            existing_room = None
        if existing_room:
            return redirect(
                "room", 
                room_name=room_name, 
                username=username
                )
        
        r = Room.objects.create(room_name=room_name)

        if item_room:
            item = Item.objects.get(pk=item_room)
            seller = item.seller.username
            item_room = ItemRoom.objects.create(
                item=item, 
                seller=seller,
                room_name=room_name
                )

        return redirect(
            "room", 
            room_name=r.room_name, 
            item_room=item_room,
            username=username
            )
    
    # Handle GET request
    rooms = Room.objects.all()
    item_rooms = ItemRoom.objects.all()

    all_rooms = [rooms, item_rooms]
    # print([all_rooms])

    context = {
        "all_rooms": all_rooms,
        }
    
    return render(request, "chat/index.html", context)

@login_required
def create_item_room(request, item_id, seller):
    item = Item.objects.get(pk=item_id)
    seller = item.seller
    room_name = f"{item.title} - {item.seller}"

    try:
        existing_room = ItemRoom.objects.get(
            item=item)
    except ItemRoom.DoesNotExist:
        existing_room = None
    if existing_room:
        return redirect(
            "room", 
            room_name=existing_room.room_name, 
            username=seller
            )

    r = ItemRoom.objects.create(
        item=item,
        seller=seller, 
        room_name=room_name
        )

    return redirect(
        "room", 
        room_name=r.room_name, 
        username=seller
        )

@login_required
def room_view(request, room_name, username):
    existing_room = Room.objects.get(
        room_name__exact=room_name)
    messages = Message.objects.filter(
        room=existing_room).order_by('-date')
    current_user = request.user
    filtered_messages = messages.filter(
        sender=current_user)
    
    context = {
        "messages": messages,
        "current_user": current_user,
        "user": username,
        "room_name": existing_room.room_name,
    }
    
    return render(request, "chat/room.html", context)
