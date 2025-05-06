# Register your models here.
from django.contrib import admin

from .models import Category, Score


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'category',
        'stars',
        'moves',
        'time_seconds',
        'completed_at',
    )
    search_fields = ('profile__owner__username', 'category__name')
