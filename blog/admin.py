from django.contrib import admin
from .models import Profile, ProfileGroup, ProfilePermission, Post, Comment, Like, Follow, Tag

class PostAdmin(admin.ModelAdmin):
    search_fields = ['title', 'author__username']
    list_display = ['title', 'author', 'publish_date', 'verification_score']
    list_filter = ['publish_date', 'verification_score']
    raw_id_fields = ['author']
    readonly_fields = ['verification_score']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'credibility_score']
    list_filter = ['credibility_score']
    readonly_fields = ['verification_history']

# Register your models here.
admin.site.register([ProfileGroup, ProfilePermission, Comment, Like, Follow, Tag])
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
