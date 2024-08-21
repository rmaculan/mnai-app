from django.contrib import admin
<<<<<<< HEAD
from .models import  Post, Comment, Likes, Follow

# Register your models here.
admin.site.register([Post, Comment, Likes, Follow])
=======
from .models import Tag, Post, Comment, Likes, Follow, Stream

# Register your models here.
admin.site.register([Tag, Post, Comment, Likes, Follow, Stream])
>>>>>>> origin/main
