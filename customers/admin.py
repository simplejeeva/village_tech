from django.contrib import admin

from customers.models import Customer


def mark_as_contacted(modeladmin, request, queryset):
    queryset.update(contacted=True)


mark_as_contacted.short_description = "Mark selected as contacted"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "place", "contacted", "created_at")
    list_filter = ("contacted", "created_at")
    search_fields = ("name", "phone", "place")
    list_editable = ("contacted",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = [mark_as_contacted]
    readonly_fields = ("created_at",)
