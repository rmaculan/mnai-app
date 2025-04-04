from django.urls import path
from . import views



urlpatterns = [
    # notes
    path('routes/', views.getRoutes),
    path('notes/', views.getNotes),
    path('note/create/', views.createNote),
    path('note/<str:pk>/update/', views.updateNote),
    path('note/<str:pk>/delete/', views.deleteNote),
    path('note/<str:pk>/', views.getNote),
]