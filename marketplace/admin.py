from django.contrib import admin

# Register your models here.
from .models import Item, CategoryModel, Conversation, ItemMessage

admin.site.register([
    Item, 
    CategoryModel, 
    Conversation, 
    ItemMessage,
    ])