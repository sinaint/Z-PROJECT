from django.contrib import admin

from .models import ScanResult


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = ("category", "target", "is_risky", "scanned_at")
    list_filter = ("category", "is_risky")
    search_fields = ("target", "detail")
