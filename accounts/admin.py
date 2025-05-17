from django.contrib import admin
from accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_active", "created_at")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("-created_at",)
    readonly_fields = ("last_login", "created_at", "updated_at")