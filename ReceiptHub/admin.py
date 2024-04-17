from django.contrib import admin

from .models import Receipt


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
# admin.site.register(Question, QuestionAdmin)
