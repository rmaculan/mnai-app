from django.urls import path
from .views import (
    getRoutes, getNotes, createNote,
    updateNote, deleteNote, getNote,
    UserRegistrationView, CustomTokenObtainPairView, UserProfileView
)



urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    
    # notes
    path('routes/', getRoutes),
    path('notes/', getNotes),
    path('note/create/', createNote),
    path('note/<str:pk>/update/', updateNote),
    path('note/<str:pk>/delete/', deleteNote),
    path('note/<str:pk>/', getNote),
]
