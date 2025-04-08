from typing import ClassVar

from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model."""

    profile_picture_url = serializers.ReadOnlyField(
        source='profile_picture.url'
    )
    owner_username = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request.user == obj.owner if request else False

    class Meta:
        model = Profile
        fields: ClassVar[list] = [
            'id',
            'owner',
            'owner_username',
            'profile_picture',
            'profile_picture_url',
            'created_at',
            'updated_at',
            'is_owner',
        ]
        read_only_fields: ClassVar[list] = [
            'id',
            'owner',
            'created_at',
            'updated_at',
        ]
