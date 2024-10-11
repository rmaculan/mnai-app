from django.shortcuts import render, redirect
from .models import Room, Message
from django.contrib.auth.decorators import login_required

@login_required
def HomeView(request):
    if request.method == "POST":
        username = request.POST["username"]
        room_name = request.POST["room"]
        try:
            existing_room = Room.objects.get(room_name__exact=room_name)
        except Room.DoesNotExist:
            existing_room = None
        
        if existing_room:
            return redirect("room", room_name=room_name, username=username)
        
        # If room doesn't exist, create a new one
        r = Room.objects.create(room_name=room_name)
        return redirect("room", room_name=r.room_name, username=username)
    
    # Handle GET request
    rooms = Room.objects.all()
    context = {"rooms": rooms}
    return render(request, "chat/home.html", context)

@login_required
def RoomView(request, room_name, username):
    existing_room = Room.objects.get(room_name__exact=room_name)
    
    # Get messages for this room
    messages = Message.objects.filter(room=existing_room).order_by('-date')
    
    # Get the authenticated user
    current_user = request.user
    
    # Filter messages for the authenticated user
    filtered_messages = messages.filter(sender=current_user)
    
    # Prepare the context
    context = {
        "messages": filtered_messages,
        # "cuurent_user": current_user,
        "current_username": username,
        "room_name": existing_room.room_name,
    }
    
    return render(request, "chat/room.html", context)
