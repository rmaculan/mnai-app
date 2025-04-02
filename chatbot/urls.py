from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.conversations, name='conversations'),
    path('chat/', views.chatbot, name='chatbot'),  # Legacy endpoint
    path('conversation/new/', views.create_conversation, name='create_conversation'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]
