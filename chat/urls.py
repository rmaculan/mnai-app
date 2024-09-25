from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    
    path('lobby/', views.lobby, name='lobby'),
    path('chats/<username>', views.get_instant_messages, name='instant_messages')
    
]


