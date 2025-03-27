from django.contrib import admin
from .models import Message, Room

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        # First delete related ItemMessages
        from marketplace.models import ItemMessage
        ItemMessage.objects.filter(room__in=[msg.room for msg in queryset]).delete()
        # Then delete the messages
        queryset.delete()


# Register your models here.

admin.site.register(Room)

