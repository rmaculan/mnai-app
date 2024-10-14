from django.contrib import admin
from .models import Room, ItemRoom, Message, MarketplaceMessage

# Register your models here.

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(ItemRoom)
admin.site.register(MarketplaceMessage)
