from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('api/conversations/', 
         views.ConversationListCreate.as_view(),
         name='conversation-list'),
    path('api/conversations/<int:pk>/', 
         views.ConversationRetrieveUpdateDestroy.as_view(), 
         name='conversation-detail'),
    path('api/conversations/<int:pk>/archive/', 
         views.ConversationArchiveView.as_view(), 
         name='conversation-archive'),
    path('api/conversations/<int:pk>/pin/', 
         views.ConversationPinView.as_view(), 
         name='conversation-pin'),
    path('api/conversations/<int:pk>/favorite/', 
         views.ConversationFavoriteView.as_view(), 
         name='conversation-favorite'),
]
