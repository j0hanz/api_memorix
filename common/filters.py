from typing import ClassVar

from django_filters import rest_framework as filters

from memorix.models import Leaderboard, Score


class ScoreFilter(filters.FilterSet):
    """Advanced filtering for Score model:"""

    completed_after = filters.DateTimeFilter(
        field_name='completed_at', lookup_expr='gte'
    )
    completed_before = filters.DateTimeFilter(
        field_name='completed_at', lookup_expr='lte'
    )
    min_moves = filters.NumberFilter(field_name='moves', lookup_expr='gte')
    max_moves = filters.NumberFilter(field_name='moves', lookup_expr='lte')
    min_time = filters.NumberFilter(
        field_name='time_seconds', lookup_expr='gte'
    )
    max_time = filters.NumberFilter(
        field_name='time_seconds', lookup_expr='lte'
    )
    category_code = filters.CharFilter(
        field_name='category__code', lookup_expr='iexact'
    )
    categories = filters.AllValuesMultipleFilter(field_name='category__code')
    player = filters.CharFilter(field_name='profile__owner__username')

    class Meta:
        model = Score
        fields: ClassVar[list[str]] = [
            'category',
            'moves',
            'time_seconds',
            'stars',
            'completed_at',
            'profile',
        ]


class LeaderboardFilter(filters.FilterSet):
    """Advanced filtering for Leaderboard model:"""

    min_rank = filters.NumberFilter(field_name='rank', lookup_expr='gte')
    max_rank = filters.NumberFilter(field_name='rank', lookup_expr='lte')
    category_code = filters.CharFilter(field_name='category__code')
    player = filters.CharFilter(field_name='score__profile__owner__username')

    class Meta:
        model = Leaderboard
        fields: ClassVar[list[str]] = ['category', 'rank']
