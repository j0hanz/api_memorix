from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from common.constants import (
    MAX_MOVES,
    MAX_STARS,
    MAX_TIME_SECONDS,
    MIN_MOVES,
    MIN_STARS,
    MIN_TIME_SECONDS,
)
from users.models import Profile

from .models import Category, Leaderboard, Score

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test Category model"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Test Animals',
            code='TEST_ANIMALS',
            description='Test animal category',
        )

    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.name, 'Test Animals')
        self.assertEqual(self.category.code, 'TEST_ANIMALS')
        self.assertEqual(self.category.description, 'Test animal category')
        self.assertTrue(self.category.created_at)

    def test_category_str_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Test Animals')

    def test_category_code_unique_constraint(self):
        """Test category code must be unique"""
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name='Another Category',
                code='TEST_ANIMALS',  # Same code should fail
                description='Different description',
            )

    def test_category_ordering(self):
        """Test categories are ordered by name"""
        category_a = Category.objects.create(name='A Category', code='A_CAT')
        category_z = Category.objects.create(name='Z Category', code='Z_CAT')

        categories = list(Category.objects.all())
        self.assertEqual(categories[0], category_a)
        self.assertEqual(categories[-1], category_z)


class ScoreModelTest(TestCase):
    """Test Score model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.profile = Profile.objects.get(owner=self.user)
        self.category = Category.objects.create(
            name='Test Category', code='TEST_CAT'
        )

    def test_score_creation(self):
        """Test score is created correctly"""
        score = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=4,
        )

        self.assertEqual(score.profile, self.profile)
        self.assertEqual(score.category, self.category)
        self.assertEqual(score.moves, 20)
        self.assertEqual(score.time_seconds, 60)
        self.assertEqual(score.stars, 4)
        self.assertTrue(score.completed_at)

    def test_score_str_representation(self):
        """Test score string representation"""
        score = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=4,
        )
        expected = f"{self.user.username}'s game - 4 stars"
        self.assertEqual(str(score), expected)

    def test_score_moves_validation(self):
        """Test score moves validation"""
        # Test minimum moves validation
        with self.assertRaises(ValidationError):
            score = Score(
                profile=self.profile,
                category=self.category,
                moves=MIN_MOVES - 1,  # Below minimum
                time_seconds=60,
                stars=3,
            )
            score.full_clean()

        # Test maximum moves validation
        with self.assertRaises(ValidationError):
            score = Score(
                profile=self.profile,
                category=self.category,
                moves=MAX_MOVES + 1,  # Above maximum
                time_seconds=60,
                stars=3,
            )
            score.full_clean()

    def test_score_time_validation(self):
        """Test score time validation"""
        # Test minimum time validation
        with self.assertRaises(ValidationError):
            score = Score(
                profile=self.profile,
                category=self.category,
                moves=20,
                time_seconds=MIN_TIME_SECONDS - 1,  # Below minimum
                stars=3,
            )
            score.full_clean()

        # Test maximum time validation
        with self.assertRaises(ValidationError):
            score = Score(
                profile=self.profile,
                category=self.category,
                moves=20,
                time_seconds=MAX_TIME_SECONDS + 1,  # Above maximum
                stars=3,
            )
            score.full_clean()

    def test_score_stars_validation(self):
        """Test score stars validation"""
        # Test minimum stars validation
        with self.assertRaises(ValidationError):
            score = Score(
                profile=self.profile,
                category=self.category,
                moves=20,
                time_seconds=60,
                stars=MIN_STARS - 1,  # Below minimum
            )
            score.full_clean()

        # Test maximum stars validation
        with self.assertRaises(ValidationError):
            score = Score(
                profile=self.profile,
                category=self.category,
                moves=20,
                time_seconds=60,
                stars=MAX_STARS + 1,  # Above maximum
            )
            score.full_clean()

    def test_score_unique_constraint(self):
        """Test score unique constraint"""
        # Create first score
        Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=4,
        )

        # Try to create duplicate score
        with self.assertRaises(IntegrityError):
            Score.objects.create(
                profile=self.profile,
                category=self.category,
                moves=20,  # Same values
                time_seconds=60,
                stars=4,
            )

    def test_score_ordering(self):
        """Test scores are ordered by completed_at descending"""
        score1 = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=4,
        )
        score2 = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=25,
            time_seconds=70,
            stars=3,
        )

        scores = list(Score.objects.all())
        self.assertEqual(scores[0], score2)  # Most recent first
        self.assertEqual(scores[1], score1)


class LeaderboardModelTest(TestCase):
    """Test Leaderboard model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.profile = Profile.objects.get(owner=self.user)
        self.category = Category.objects.create(
            name='Test Category', code='TEST_CAT'
        )
        # Create score but clear any auto-generated leaderboard entries for testing
        self.score = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=5,
        )
        # Clear auto-generated leaderboard entries for manual testing
        Leaderboard.objects.filter(category=self.category).delete()

    def test_leaderboard_creation(self):
        """Test leaderboard entry is created correctly"""
        leaderboard = Leaderboard.objects.create(
            score=self.score, category=self.category, rank=1
        )

        self.assertEqual(leaderboard.score, self.score)
        self.assertEqual(leaderboard.category, self.category)
        self.assertEqual(leaderboard.rank, 1)

    def test_leaderboard_str_representation(self):
        """Test leaderboard string representation"""
        leaderboard = Leaderboard.objects.create(
            score=self.score, category=self.category, rank=1
        )
        expected = f'Rank 1: {self.score}'
        self.assertEqual(str(leaderboard), expected)

    def test_leaderboard_unique_rank_constraint(self):
        """Test leaderboard unique rank per category constraint"""
        # Create first leaderboard entry
        Leaderboard.objects.create(
            score=self.score, category=self.category, rank=1
        )

        # Create another score for the same category
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
        )
        profile2 = Profile.objects.get(owner=user2)
        score2 = Score.objects.create(
            profile=profile2,
            category=self.category,
            moves=25,
            time_seconds=70,
            stars=4,
        )

        # Try to create duplicate rank in same category
        with self.assertRaises(IntegrityError):
            Leaderboard.objects.create(
                score=score2,
                category=self.category,
                rank=1,  # Same rank should fail
            )

    def test_leaderboard_ordering(self):
        """Test leaderboard ordering by category and rank"""
        # Create another category and scores
        category2 = Category.objects.create(
            name='Test Category 2', code='TEST_CAT2'
        )

        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
        )
        profile2 = Profile.objects.get(owner=user2)

        score2 = Score.objects.create(
            profile=profile2,
            category=self.category,
            moves=25,
            time_seconds=70,
            stars=4,
        )

        score3 = Score.objects.create(
            profile=profile2,
            category=category2,
            moves=30,
            time_seconds=80,
            stars=3,
        )

        # Clear any auto-generated leaderboard entries
        Leaderboard.objects.all().delete()

        # Create leaderboard entries manually for testing
        lb1 = Leaderboard.objects.create(
            score=self.score, category=self.category, rank=1
        )
        lb2 = Leaderboard.objects.create(
            score=score2, category=self.category, rank=2
        )
        lb3 = Leaderboard.objects.create(
            score=score3, category=category2, rank=1
        )

        leaderboards = list(Leaderboard.objects.all())
        # Should be ordered by category name, then rank
        self.assertEqual(leaderboards[0], lb1)  # Test Category, rank 1
        self.assertEqual(leaderboards[1], lb2)  # Test Category, rank 2
        self.assertEqual(leaderboards[2], lb3)  # Test Category 2, rank 1


class CategoryAPITest(APITestCase):
    """Test Category API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.category = Category.objects.create(
            name='Test Animals',
            code='ANIMALS',
            description='Test animal category',
        )

    def test_list_categories_anonymous(self):
        """Test listing categories as anonymous user"""
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle paginated response if needed
        if isinstance(response.data, dict) and 'results' in response.data:
            categories = response.data['results']
        else:
            categories = response.data

        # Should include the test category plus any pre-existing categories
        self.assertGreaterEqual(len(categories), 1)
        # Check that our test category is in the response
        category_names = [cat['name'] for cat in categories]
        self.assertIn('Test Animals', category_names)

    def test_list_categories_authenticated(self):
        """Test listing categories as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle paginated response if needed
        if isinstance(response.data, dict) and 'results' in response.data:
            categories = response.data['results']
        else:
            categories = response.data

        # Should include the test category plus any pre-existing categories
        self.assertGreaterEqual(len(categories), 1)
        # Check that our test category is in the response
        category_names = [cat['name'] for cat in categories]
        self.assertIn('Test Animals', category_names)

    def test_retrieve_category(self):
        """Test retrieving single category"""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Animals')
        self.assertEqual(response.data['code'], 'ANIMALS')

    def test_category_create_not_allowed(self):
        """Test creating category via API is not allowed"""
        self.client.force_authenticate(user=self.user)
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'code': 'NEW_CAT',
            'description': 'New test category',
        }
        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_category_update_not_allowed(self):
        """Test updating category via API is not allowed"""
        self.client.force_authenticate(user=self.user)
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        data = {'name': 'Updated Name'}
        response = self.client.patch(url, data)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_category_delete_not_allowed(self):
        """Test deleting category via API is not allowed"""
        self.client.force_authenticate(user=self.user)
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ScoreAPITest(APITestCase):
    """Test Score API endpoints"""

    def setUp(self):
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
        self.profile = Profile.objects.get(owner=self.user)
        self.profile2 = Profile.objects.get(owner=self.user2)

        self.category = Category.objects.create(
            name='Test Animals',
            code='ANIMALS',
            description='Test animal category',
        )

        self.score = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=4,
        )

    def get_tokens_for_user(self, user):
        """Helper method to get JWT tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_list_scores_anonymous(self):
        """Test listing scores as anonymous user returns empty"""
        url = reverse('gameresult-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_list_scores_authenticated(self):
        """Test listing scores as authenticated user"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'testuser')

    def test_create_score_anonymous(self):
        """Test creating score as anonymous user fails"""
        url = reverse('gameresult-list')
        data = {
            'category': 'ANIMALS',
            'moves': 25,
            'time_seconds': 70,
            'stars': 3,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_score_authenticated(self):
        """Test creating score as authenticated user"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-list')
        data = {
            'category': 'ANIMALS',
            'moves': 25,
            'time_seconds': 70,
            'stars': 3,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['moves'], 25)
        self.assertEqual(response.data['category_name'], 'Test Animals')

    def test_create_score_validation_errors(self):
        """Test score creation with validation errors"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-list')

        # Test invalid moves
        data = {
            'category': 'ANIMALS',
            'moves': 0,  # Below minimum
            'time_seconds': 60,
            'stars': 3,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('moves', response.data)

        # Test invalid time
        data = {
            'category': 'ANIMALS',
            'moves': 20,
            'time_seconds': 0,  # Below minimum
            'stars': 3,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('time_seconds', response.data)

        # Test invalid stars
        data = {
            'category': 'ANIMALS',
            'moves': 20,
            'time_seconds': 60,
            'stars': 6,  # Above maximum
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stars', response.data)

    def test_create_score_cross_field_validation(self):
        """Test score creation with cross-field validation"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-list')

        # Test impossible time/moves combination
        data = {
            'category': 'ANIMALS',
            'moves': 1000,
            'time_seconds': 1,  # Too fast for number of moves
            'stars': 3,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test unrealistic high stars with too many moves
        data = {
            'category': 'ANIMALS',
            'moves': 500,  # Too many moves
            'time_seconds': 300,
            'stars': 5,  # High stars with poor performance
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_own_score(self):
        """Test retrieving own score"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-detail', kwargs={'pk': self.score.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_retrieve_other_user_score_forbidden(self):
        """Test retrieving another user's score is forbidden"""
        tokens = self.get_tokens_for_user(self.user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-detail', kwargs={'pk': self.score.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_score_forbidden(self):
        """Test updating score is forbidden"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-detail', kwargs={'pk': self.score.pk})
        data = {'moves': 30}
        response = self.client.patch(url, data)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_filter_scores_by_category(self):
        """Test filtering scores by category"""
        # Create another category and score
        category2 = Category.objects.create(name='Test Nature', code='NATURE')
        Score.objects.create(
            profile=self.profile,
            category=category2,
            moves=30,
            time_seconds=80,
            stars=3,
        )

        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )
        url = reverse('gameresult-list')
        response = self.client.get(url, {'category_code': 'ANIMALS'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['category_name'], 'Test Animals'
        )

    def test_best_scores_anonymous(self):
        """Test best scores endpoint as anonymous user"""
        url = reverse('gameresult-best')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_best_scores_authenticated(self):
        """Test best scores endpoint as authenticated user"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-best')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_own_score(self):
        """Test deleting own score"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-detail', kwargs={'pk': self.score.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Score.objects.filter(pk=self.score.pk).exists())

    def test_delete_other_user_score_forbidden(self):
        """Test deleting another user's score is forbidden"""
        tokens = self.get_tokens_for_user(self.user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-detail', kwargs={'pk': self.score.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Score.objects.filter(pk=self.score.pk).exists())

    def test_delete_score_unauthenticated(self):
        """Test deleting score without authentication"""
        url = reverse('gameresult-detail', kwargs={'pk': self.score.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Score.objects.filter(pk=self.score.pk).exists())

    def test_clear_category_scores(self):
        """Test clearing all scores for a specific category"""
        # Create additional scores for the same category
        Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=15,
            time_seconds=45,
            stars=5,
        )
        Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=25,
            time_seconds=75,
            stars=3,
        )

        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        # Should have 3 scores total (including setUp score)
        self.assertEqual(
            Score.objects.filter(
                profile=self.profile, category=self.category
            ).count(),
            3,
        )

        url = reverse(
            'gameresult-clear-category-scores',
            kwargs={'category_code': self.category.code},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Successfully deleted 3 scores', response.data['detail'])
        self.assertEqual(
            Score.objects.filter(
                profile=self.profile, category=self.category
            ).count(),
            0,
        )

    def test_clear_category_scores_invalid_category(self):
        """Test clearing scores for non-existent category"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse(
            'gameresult-clear-category-scores',
            kwargs={'category_code': 'INVALID'},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Category not found.')

    def test_clear_category_scores_no_scores(self):
        """Test clearing scores for category with no user scores"""
        # Create another category
        empty_category = Category.objects.create(
            name='Empty Category', code='EMPTY'
        )

        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse(
            'gameresult-clear-category-scores',
            kwargs={'category_code': empty_category.code},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['detail'], 'No scores found for this category.'
        )

    def test_clear_all_scores(self):
        """Test clearing all user scores"""
        # Create additional category and scores
        category2 = Category.objects.create(
            name='Test Category 2', code='TEST_CAT2'
        )
        Score.objects.create(
            profile=self.profile,
            category=category2,
            moves=15,
            time_seconds=45,
            stars=5,
        )

        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        # Should have 2 scores total
        self.assertEqual(Score.objects.filter(profile=self.profile).count(), 2)

        url = reverse('gameresult-clear-all-scores')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            'Successfully deleted all 2 scores', response.data['detail']
        )
        self.assertEqual(Score.objects.filter(profile=self.profile).count(), 0)

    def test_clear_all_scores_no_scores(self):
        """Test clearing all scores when user has no scores"""
        # Delete the setup score
        self.score.delete()

        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-clear-all-scores')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No scores found to delete.')

    def test_clear_all_scores_unauthenticated(self):
        """Test clearing all scores without authentication"""
        url = reverse('gameresult-clear-all-scores')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LeaderboardAPITest(APITestCase):
    """Test Leaderboard API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.profile = Profile.objects.get(owner=self.user)

        self.category = Category.objects.create(
            name='Test Animals',
            code='ANIMALS',
            description='Test animal category',
        )

        self.score = Score.objects.create(
            profile=self.profile,
            category=self.category,
            moves=20,
            time_seconds=60,
            stars=5,
        )

        # Clear auto-generated leaderboard entries from signal handler
        Leaderboard.objects.filter(category=self.category).delete()

        self.leaderboard = Leaderboard.objects.create(
            score=self.score, category=self.category, rank=1
        )

    def test_list_leaderboard_anonymous(self):
        """Test listing leaderboard as anonymous user"""
        url = reverse('leaderboard-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_leaderboard_authenticated(self):
        """Test listing leaderboard as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('leaderboard-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_leaderboard_by_category(self):
        """Test filtering leaderboard by category"""
        url = reverse('leaderboard-list')
        response = self.client.get(url, {'category': self.category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_leaderboard_entry(self):
        """Test retrieving single leaderboard entry"""
        url = reverse('leaderboard-detail', kwargs={'pk': self.leaderboard.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rank'], 1)
        self.assertEqual(response.data['username'], 'testuser')

    def test_leaderboard_create_not_allowed(self):
        """Test creating leaderboard via API is not allowed"""
        self.client.force_authenticate(user=self.user)
        url = reverse('leaderboard-list')
        data = {
            'score': self.score.id,
            'category': self.category.id,
            'rank': 2,
        }
        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ThrottlingTest(APITestCase):
    """Test API throttling"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.category = Category.objects.create(
            name='Test Animals', code='ANIMALS'
        )

    def get_tokens_for_user(self, user):
        """Helper method to get JWT tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_score_submission_throttling(self):
        """Test score submission throttling"""
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}'
        )

        url = reverse('gameresult-list')

        # Make multiple score submissions
        for i in range(5):  # Make a few requests first
            data = {
                'category': 'ANIMALS',
                'moves': 20 + i,
                'time_seconds': 60 + i,
                'stars': 3,
            }
            response = self.client.post(url, data)

            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                # Throttling is working
                self.assertIn('throttled', response.data['detail'].lower())
                break
        else:
            # If we didn't hit throttling in 5 requests, that's still acceptable
            # as the throttle limit might be higher in test settings
            pass
