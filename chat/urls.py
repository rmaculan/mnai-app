from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="chat-login"),
    # path('<str:room_name>/<int:item>/<str:seller>/', views.create_item_room, name='create_item_room'),
    # path("", views.create_room, name="create_room"),
    path("<str:room_name>/<str:username>/", views.room_view, name="room"),
]
