from django.contrib import admin
from .models import  Post, Comment, Likes, Follow

# Register your models here.
admin.site.register([Post, Comment, Likes, Follow])