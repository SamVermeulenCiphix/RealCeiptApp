from django.contrib import admin

from .models import Question, Choice, Receipt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


class ReceiptAdmin(admin.ModelAdmin):
    readonly_fields = ["file_displayname", "file_uuid", "total_amount", "file_fullpath", "url"]
    fieldsets = [
        (None, {"fields": ["file_displayname"]}),
        ("File information", {"fields": ["file_uuid", "total_amount", "file_fullpath", "url"], "classes": ["wide"]}),
    ]
    # inlines = [ChoiceInline]
    list_display = ["file_displayname", "upload_date", "total_amount", "file_uuid"]
    list_filter = ["upload_date"]
    search_fields = ["file_displayname"]

admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Question, QuestionAdmin)
