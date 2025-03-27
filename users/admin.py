from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the Profile model."""

    list_display = ('owner', 'created_at', 'updated_at')
    search_fields = ('owner__username',)
