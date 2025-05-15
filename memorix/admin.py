from django.contrib import admin

from .models import Category, Leaderboard, Score


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


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = (
        'rank',
        'category',
        'score',
        'get_username',
        'get_stars',
    )
    list_filter = ('category',)
    search_fields = ('score__profile__owner__username', 'category__name')

    def get_username(self, obj):
        return obj.score.profile.owner.username

    get_username.short_description = 'Username'

    def get_stars(self, obj):
        return obj.score.stars

    get_stars.short_description = 'Stars'
