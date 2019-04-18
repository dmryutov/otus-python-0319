from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    User model admin view
    """
    list_display = ('id', 'username', 'email', 'avatar')
    search_fields = ('username', 'email')
