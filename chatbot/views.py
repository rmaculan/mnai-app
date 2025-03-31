from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from .utils import get_provider
from django.contrib.auth.models import User
from .models import Chat, Conversation
from django.utils import timezone
from django.conf import settings
from .serializers import ConversationSerializer

class ConversationListCreate(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Conversation.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'archived':
            queryset = queryset.filter(is_archived=True)
        elif status == 'pinned':
            queryset = queryset.filter(is_pinned=True)
        elif status == 'favorite':
            queryset = queryset.filter(is_favorite=True)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ConversationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )

    def perform_destroy(self, instance):
        # Soft delete implementation
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()

class ConversationArchiveView(generics.UpdateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(is_archived=not serializer.instance.is_archived)

class ConversationPinView(generics.UpdateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(is_pinned=not serializer.instance.is_pinned)

class ConversationFavoriteView(generics.UpdateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(is_favorite=not serializer.instance.is_favorite)

def ask_openai(message, provider_name="openai"):
    provider = get_provider(provider_name)
    response = provider.chat_completion([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ])
    
    # Handle different provider response formats
    if provider_name == "openai":
        return response.choices[0].message.content.strip()
    elif provider_name == "deepseek":
        return response.choices[0].message.content.strip()
    else:
        return str(response)  # Fallback for unknown providers

def chatbot(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    conversations = Conversation.objects.filter(user=request.user)
    active_conversation = conversations.filter(is_active=True).first()

    if request.method == 'POST':
        message = request.POST.get('message')
        provider = request.POST.get('provider', 'openai')
        
        if not active_conversation:
            active_conversation = Conversation.objects.create(
                title=f"Chat with {request.user.username}",
                user=request.user,
                provider=provider
            )
        
        response = ask_openai(message, provider)

        chat = Chat(
            conversation=active_conversation,
            user=request.user,
            message=message,
            response=response,
            created_at=timezone.now()
        )
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    
    chats = []
    if active_conversation:
        chats = Chat.objects.filter(conversation=active_conversation).order_by('created_at')
    
    return render(request, 'chatbot/chatbot.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'chats': chats
    })

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'chatbot/login.html', {'error_message': error_message})
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
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'chatbot/register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'chatbot/register.html', {'error_message': error_message})
    return render(request, 'chatbot/register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
