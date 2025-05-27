from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test the Profile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

    def test_profile_creation_via_signal(self):
        """Test that a profile is automatically created when a user is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_str_representation(self):
        """Test the string representation of a profile"""
        expected = f"{self.user}'s profile"
        self.assertEqual(str(self.user.profile), expected)

    def test_profile_ordering(self):
        """Test that profiles are ordered by creation date (newest first)"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
        )
        profiles = Profile.objects.all()
        self.assertEqual(profiles.first(), user2.profile)
        self.assertEqual(profiles.last(), self.user.profile)

    def test_profile_default_picture(self):
        """Test that profile has default picture"""
        from common.constants import DEFAULT_PROFILE_PICTURE

        self.assertEqual(
            str(self.user.profile.profile_picture), DEFAULT_PROFILE_PICTURE
        )

    def test_profile_timestamps(self):
        """Test that profile has created_at and updated_at timestamps"""
        profile = self.user.profile
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    def test_profile_deletion_cascades_from_user(self):
        """Test that profile is deleted when user is deleted"""
        profile_id = self.user.profile.id
        self.user.delete()
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())


class ProfileAPITest(APITestCase):
    """Test the Profile API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
        )
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_list_profiles_unauthenticated(self):
        """Test that unauthenticated users can list profiles"""
        url = reverse('profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_profiles_authenticated(self):
        """Test that authenticated users can list profiles"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        url = reverse('profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_profile(self):
        """Test retrieving a specific profile"""
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner_username'], 'testuser')
        self.assertEqual(response.data['owner'], self.user.id)

    def test_update_own_profile_authenticated(self):
        """Test that users can update their own profile"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})

        # Try to update profile picture (mock data since we don't have actual image)
        data = {'profile_picture': 'test_image_url'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_profile_forbidden(self):
        """Test that users cannot update other users' profiles"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        url = reverse('profile-detail', kwargs={'pk': self.user2.profile.id})

        data = {'profile_picture': 'test_image_url'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_profile_not_allowed(self):
        """Test that profiles cannot be deleted via API"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})
        response = self.client.delete(url)
        # Should not be allowed or should return 405 Method Not Allowed
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED],
        )

    def test_profile_serializer_fields(self):
        """Test that profile serializer returns expected fields"""
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})
        response = self.client.get(url)

        expected_fields = [
            'id',
            'owner',
            'owner_username',
            'profile_picture',
            'profile_picture_url',
            'created_at',
            'updated_at',
            'is_owner',
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_is_owner_field_authenticated(self):
        """Test that is_owner field works correctly for authenticated users"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        # Check own profile
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})
        response = self.client.get(url)
        self.assertTrue(response.data['is_owner'])

        # Check other user's profile
        url = reverse('profile-detail', kwargs={'pk': self.user2.profile.id})
        response = self.client.get(url)
        self.assertFalse(response.data['is_owner'])

    def test_is_owner_field_unauthenticated(self):
        """Test that is_owner field is False for unauthenticated users"""
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})
        response = self.client.get(url)
        self.assertFalse(response.data['is_owner'])

    def test_profile_read_only_fields(self):
        """Test that read-only fields cannot be updated"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        url = reverse('profile-detail', kwargs={'pk': self.user.profile.id})

        original_created_at = self.user.profile.created_at
        data = {
            'owner': self.user2.id,  # Should not change
            'created_at': '2020-01-01T00:00:00Z',  # Should not change
            'id': 999,  # Should not change
        }
        response = self.client.patch(url, data, format='json')

        # Refresh from database
        self.user.profile.refresh_from_db()

        # Check that read-only fields weren't changed
        self.assertEqual(self.user.profile.owner.id, self.user.id)
        self.assertEqual(self.user.profile.created_at, original_created_at)
        self.assertNotEqual(self.user.profile.id, 999)
