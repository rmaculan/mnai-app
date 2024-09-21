from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='chat'),
    path('chats/<username>', views.get_instant_messages, name='instant_messages')
]

