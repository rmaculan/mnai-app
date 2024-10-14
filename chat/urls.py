from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="chat-login"),
    path("<str:room_name>/<str:username>/", views.room_view, name="room"),
    path("create/", views.create_room, name="create_room"),
    # path("manage/<str:room_name>/", views.manage_room, name="manage_room"),
    # path("delete/<str:room_name>/", views.delete_room, name="delete_room"),
    
]
