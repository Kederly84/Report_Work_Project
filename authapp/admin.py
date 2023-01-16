from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authapp.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_per_page = 10
    list_filter = ('username', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name')
    show_full_result_count = False
    # This line will fix the problem in the admin panel that you suffer every time
    filter_horizontal = ('groups', 'user_permissions')
