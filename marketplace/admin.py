from django.contrib import admin

# Register your models here.
from .models import Item, CategoryModel, UserProfile, Conversation,UserMessage

admin.site.register([
    Item, 
    CategoryModel, 
    UserProfile, 
    Conversation, 
    UserMessage,
    ])