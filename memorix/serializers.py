from typing import ClassVar

from rest_framework import serializers
from rest_framework.validators import ValidationError

from common.constants import (
    HIGH_STAR_THRESHOLD,
    MAX_MOVES,
    MAX_MOVES_FOR_HIGH_STARS,
    MAX_STARS,
    MAX_TIME_SECONDS,
    MIN_MOVES,
    MIN_STARS,
    MIN_TIME_SECONDS,
)
from common.datetime import format_completed_at
from common.score import prepare_score_data

from .models import Category, Leaderboard, Score


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='profile.owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    category = serializers.CharField(write_only=True)
    profile_picture_url = serializers.ReadOnlyField(
        source='profile.profile_picture.url'
    )

    class Meta:
        model = Score
        fields: ClassVar[list] = [
            'id',
            'profile',
            'username',
            'profile_picture_url',
            'category',
            'category_name',
            'moves',
            'time_seconds',
            'stars',
            'completed_at',
        ]
        read_only_fields: ClassVar[list] = [
            'id',
            'completed_at',
            'profile',
        ]

    def validate_moves(self, value):
        """Security: Validate moves are within realistic range"""
        if not MIN_MOVES <= value <= MAX_MOVES:
            raise ValidationError(
                f'Moves must be between {MIN_MOVES} and {MAX_MOVES}'
            )
        return value

    def validate_time_seconds(self, value):
        """Security: Validate time is within realistic range"""
        if not MIN_TIME_SECONDS <= value <= MAX_TIME_SECONDS:
            raise ValidationError(
                f'Time must be between {MIN_TIME_SECONDS} and '
                f'{MAX_TIME_SECONDS} seconds'
            )
        return value

    def validate_stars(self, value):
        """Security: Validate stars are within game range"""
        if not MIN_STARS <= value <= MAX_STARS:
            raise ValidationError(
                f'Stars must be between {MIN_STARS} and {MAX_STARS}'
            )
        return value

    def validate(self, attrs):
        """Security: Cross-field validation for realistic game data"""
        moves = attrs.get('moves')
        time_seconds = attrs.get('time_seconds')
        stars = attrs.get('stars')
        if moves and time_seconds:
            min_time_per_move = 0.1
            if time_seconds < (moves * min_time_per_move):
                raise ValidationError('Time too short for the number of moves')
        if (
            stars
            and stars >= HIGH_STAR_THRESHOLD
            and moves
            and moves > MAX_MOVES_FOR_HIGH_STARS
        ):
            raise ValidationError(
                'High star rating with excessive moves is unrealistic'
            )

        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['completed_at'] = format_completed_at(
            instance.completed_at
        )
        return representation

    def create(self, validated_data):
        prepared_data = prepare_score_data(validated_data, self.context)
        lookup_fields = {
            'profile': prepared_data.get('profile'),
            'category': prepared_data.get('category'),
            'moves': prepared_data.get('moves'),
            'time_seconds': prepared_data.get('time_seconds'),
            'stars': prepared_data.get('stars'),
        }
        instance, created = Score.objects.update_or_create(
            **lookup_fields, defaults={}
        )
        return instance


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='score.profile.owner.username')
    profile_id = serializers.ReadOnlyField(source='score.profile.id')
    profile_picture_url = serializers.ReadOnlyField(
        source='score.profile.profile_picture.url'
    )
    category_name = serializers.ReadOnlyField(source='category.name')
    category_code = serializers.ReadOnlyField(source='category.code')
    moves = serializers.ReadOnlyField(source='score.moves')
    time_seconds = serializers.ReadOnlyField(source='score.time_seconds')
    stars = serializers.ReadOnlyField(source='score.stars')
    completed_at = serializers.SerializerMethodField()

    class Meta:
        model = Leaderboard
        fields: ClassVar[list] = [
            'id',
            'rank',
            'username',
            'profile_id',
            'profile_picture_url',
            'category',
            'category_name',
            'category_code',
            'moves',
            'time_seconds',
            'stars',
            'completed_at',
        ]

    def get_completed_at(self, obj):
        return format_completed_at(obj.score.completed_at)
