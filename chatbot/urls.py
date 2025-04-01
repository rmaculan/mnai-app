from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('sessions/', views.chat_sessions_list, name='chat_sessions_list'),
    path('sessions/create/', views.chat_session_create, name='chat_session_create'),
    path('sessions/delete/<int:session_id>/', views.chat_session_delete, name='chat_session_delete'),
    path('payment_settings/', views.payment_settings, name='payment_settings'),
]
