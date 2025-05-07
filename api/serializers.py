from dj_rest_auth.serializers import UserDetailsSerializer, JWTSerializer as BaseJWTSerializer
from rest_framework import serializers


class CurrentUserSerializer(UserDetailsSerializer):
    """Serializer for the current authenticated user"""

    profile_id = serializers.ReadOnlyField(source='profile.id')
    profile_image = serializers.ReadOnlyField(
        source='profile.profile_picture.url'
    )

    class Meta(UserDetailsSerializer.Meta):
        fields = (
            *UserDetailsSerializer.Meta.fields,
            'profile_id',
            'profile_image',
        )

class PublicJWTSerializer(BaseJWTSerializer):
    """Serializer for JWT tokens with refresh token included"""
    @property
    def data(self):
        data = super().data
        data["refresh"] = self.token.get("refresh")
        return data
