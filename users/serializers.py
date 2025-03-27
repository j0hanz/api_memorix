from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model."""

    profile_picture_url = serializers.ReadOnlyField(
        source='profile_picture.url'
    )
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Profile
        fields = [
            'id',
            'owner',
            'owner_username',
            'profile_picture',
            'profile_picture_url',
            'created_at',
            'updated_at',
        ]
