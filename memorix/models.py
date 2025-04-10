from typing import ClassVar

from django.db import models

from users.models import Profile


class Category(models.Model):
    """Model for game categories"""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
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
    moves = models.PositiveIntegerField()
    time_seconds = models.PositiveIntegerField()
    stars = models.PositiveSmallIntegerField()
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
