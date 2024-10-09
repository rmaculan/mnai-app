from django.contrib import admin

# Register your models here.
from .models import Item, CategoryModel, ItemMessage

admin.site.register([
    Item, 
    CategoryModel, 
    ItemMessage,
    ])