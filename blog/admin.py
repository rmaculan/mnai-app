from django.contrib import admin
from .models import Profile, ProfileGroup, ProfilePermission, Post, Comment, Likes, Follow, Tag

# Register your models here.
admin.site.register([Profile, ProfileGroup, ProfilePermission, Post, Comment, Likes, Follow, Tag])
