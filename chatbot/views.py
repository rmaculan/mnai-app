from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from openai import OpenAI
import os
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Chat, Conversation

from django.utils import timezone
from django.conf import settings

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def ask_openai(message):
    response = client.chat.completions.create(
        model = "gpt-4",
        messages=[
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    
    answer = response.choices[0].message.content.strip()
    return answer

@login_required
def conversations(request):
    """View to list all conversations for the current user"""
    user_conversations = Conversation.objects.filter(user=request.user)
    return render(request, 'chatbot/conversations.html', {'conversations': user_conversations})

@login_required
def create_conversation(request):
    """View to create a new conversation"""
    if request.method == 'POST':
        title = request.POST.get('title', 'New Conversation')
        conversation = Conversation(
            user=request.user, 
            title=title,
            provider="openai",  # Required field
            is_active=True,     # Required field
            is_archived=False,  # Required field
            is_favorite=False,  # Required field
            is_pinned=False     # Required field
        )
        conversation.save()
        return redirect('chatbot:conversation_detail', conversation_id=conversation.id)
    return render(request, 'chatbot/create_conversation.html')

@login_required
def delete_conversation(request, conversation_id):
    """View to delete a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        conversation.delete()
        return redirect('chatbot:conversations')
    return render(request, 'chatbot/delete_conversation.html', {'conversation': conversation})

@login_required
def conversation_detail(request, conversation_id):
    """View to display a specific conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    chats = Chat.objects.filter(conversation=conversation)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        
        chat = Chat(
            user=request.user,
            conversation=conversation,
            message=message,
            response=response,
            created_at=timezone.now(),
            is_function_call=False,  # Add this required field
            function_name=None,
            function_args=None,
            function_result=None
        )
        chat.save()
        
        # Update the conversation's updated_at timestamp
        conversation.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'message': message, 'response': response})
    
    return render(request, 'chatbot/conversation_detail.html', {
        'conversation': conversation,
        'chats': chats
    })

# Legacy view, now redirects to the conversations list
def chatbot(request):
    """Original chatbot view, now redirects to conversations"""
    if not request.user.is_authenticated:
        return redirect('chatbot:login')
    
    # If this is an AJAX request, handle it specially
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        message = request.POST.get('message')
        response = ask_openai(message)
        
        # Create a default conversation if one doesn't exist
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            defaults={
                'title': 'Default Conversation',
                'provider': 'openai',  # Required field
                'is_active': True,     # Required field
                'is_archived': False,  # Required field
                'is_favorite': False,  # Required field
                'is_pinned': False     # Required field
            }
        )
        
        chat = Chat(
            user=request.user,
            conversation=conversation,
            message=message,
            response=response,
            created_at=timezone.now(),
            is_function_call=False,  # Add this required field
            function_name=None,
            function_args=None,
            function_result=None
        )
        chat.save()
        
        return JsonResponse({'message': message, 'response': response})
    
    # Normal request, redirect to conversations list
    return redirect('chatbot:conversations')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot:conversations')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'chatbot/login.html', {'error_message': error_message})
    else:
        return render(request, 'chatbot/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot:conversations')
            except:
                error_message = 'Error creating account'
                return render(request, 'chatbot/register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'chatbot/register.html', {'error_message': error_message})
    return render(request, 'chatbot/register.html')

def logout(request):
    auth.logout(request)
    return redirect('chatbot:login')
