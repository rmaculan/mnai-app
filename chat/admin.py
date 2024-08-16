from django.contrib import admin
from .models import Author, Message

# Register your models here.
admin.site.register(Author, Message)

