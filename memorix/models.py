from typing import ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from common.constants import (
    CATEGORY_CODE_MAX_LENGTH,
    CATEGORY_DESCRIPTION_MAX_LENGTH,
    CATEGORY_NAME_MAX_LENGTH,
    MAX_LEADERBOARD_RANK,
    MAX_MOVES,
    MAX_STARS,
    MAX_TIME_SECONDS,
    MIN_MOVES,
    MIN_STARS,
    MIN_TIME_SECONDS,
)
from users.models import Profile


class Category(models.Model):
    """Model for game categories"""

    name = models.CharField(max_length=CATEGORY_NAME_MAX_LENGTH)
    code = models.CharField(max_length=CATEGORY_CODE_MAX_LENGTH, unique=True)
    description = models.TextField(
        blank=True, max_length=CATEGORY_DESCRIPTION_MAX_LENGTH
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Game Categories'
        ordering: ClassVar[list[str]] = ['name']

    def __str__(self):
        return self.name


class Score(models.Model):
    """Model for game results"""

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='game_results'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='results'
    )
    moves = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_MOVES), MaxValueValidator(MAX_MOVES)]
    )
    time_seconds = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_TIME_SECONDS),
            MaxValueValidator(MAX_TIME_SECONDS),
        ]
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_STARS), MaxValueValidator(MAX_STARS)]
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar[list[str]] = ['-completed_at']
        constraints: ClassVar[list[models.UniqueConstraint]] = [
            models.UniqueConstraint(
                fields=[
                    'profile',
                    'category',
                    'moves',
                    'time_seconds',
                    'stars',
                ],
                name='unique_game_result',
            )
        ]

    def __str__(self):
        return f"{self.profile.owner.username}'s game - {self.stars} stars"


class Leaderboard(models.Model):
    """Model for leaderboard entries"""

    score = models.OneToOneField(
        Score, on_delete=models.CASCADE, related_name='leaderboard_entry'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='leaderboard_entries'
    )
    rank = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(MAX_LEADERBOARD_RANK),
        ]
    )

    class Meta:
        ordering: ClassVar[list[str]] = ['category', 'rank']
        constraints: ClassVar[list[models.UniqueConstraint]] = [
            models.UniqueConstraint(
                fields=['category', 'rank'], name='unique_leaderboard_rank'
            )
        ]
        verbose_name_plural = 'Leaderboards'

    def __str__(self):
        return f'Rank {self.rank}: {self.score}'


@receiver(post_save, sender=Score)
def update_leaderboard(sender, instance, created, **kwargs):
    """Update leaderboard when a new score is saved."""
    from common.leaderboard import update_category_leaderboard

    if created or kwargs.get('update_fields'):
        update_category_leaderboard(instance.category)
