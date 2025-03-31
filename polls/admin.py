from django.contrib import admin

from .models import Choice, Question, VoteRecord

# register models
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text", "question_type", "post"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "question_type", "post", "pub_date", "was_published_recently"]
    list_filter = ["pub_date", "question_type"]
    search_fields = ["question_text", "post__title"]
    autocomplete_fields = ["post"]

class VoteRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "question", "choice", "voted_at"]
    list_filter = ["voted_at"]
    search_fields = ["user__username", "question__question_text"]
    raw_id_fields = ["user", "question", "choice"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(VoteRecord, VoteRecordAdmin)
