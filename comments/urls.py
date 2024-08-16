from django.urls import path
from . import views

urlpatterns = [
    path("", views.comments, name="comments"),
    path("reply/<int:comment_id>", views.reply, name="reply"),
]
