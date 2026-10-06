"""Настройка админки для приложения users."""

from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "phone_number", "country", "is_active", "is_staff")
    search_fields = ("email", "phone_number", "country")
    list_filter = ("is_active", "is_staff")
