from django.contrib import admin

from .models import Receipt

# displays the receipt models in the admin panel
# for data integrity of employees' receipts, all fields are read-only
class ReceiptAdmin(admin.ModelAdmin):
    readonly_fields = ["file_displayname", "file_uuid", "total_amount", "file_fullpath", "url"]
    fieldsets = [
        (None, {"fields": ["file_displayname"]}),
        ("File information", {"fields": ["file_uuid", "total_amount", "file_fullpath", "url"], "classes": ["wide"]}),
    ]
    list_display = ["file_displayname", "upload_date", "total_amount", "file_uuid"]
    list_filter = ["upload_date"]
    search_fields = ["file_displayname"]

admin.site.register(Receipt, ReceiptAdmin)