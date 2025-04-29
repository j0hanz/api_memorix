from typing import ClassVar

from rest_framework import serializers

from common.datetime_utils import format_completed_at
from common.score_utils import prepare_score_data

from .models import Category, Score


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='profile.owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    category = serializers.CharField(write_only=True)

    class Meta:
        model = Score
        fields: ClassVar[list] = [
            'id',
            'profile',
            'username',
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
