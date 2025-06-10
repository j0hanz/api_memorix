from dj_rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from dj_rest_auth.serializers import (
    PasswordChangeSerializer,
    UserDetailsSerializer,
)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


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


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout with JWT blacklisting"""

    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate and blacklist the refresh token"""
        refresh_token = attrs['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError(
                _('Invalid refresh token or token already blacklisted.')
            )
        return attrs


class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    """Serializer for changing user passwords with additional validation"""

    def validate_old_password(self, value):
        """Validate that the old password is correct"""
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(_('Invalid current password.'))
        return value

    def validate(self, attrs):
        """Additional validation"""
        attrs = super().validate(attrs)

        old_password = attrs.get('old_password')
        new_password1 = attrs.get('new_password1')

        if old_password and new_password1 and old_password == new_password1:
            raise serializers.ValidationError(
                _('New password must be different from current password.')
            )

        return attrs
