from django.contrib import admin
from .models import Tag, Post, Comment, Likes, Follow, Stream

# Register your models here.
admin.site.register([Tag, Post, Comment, Likes, Follow, Stream])