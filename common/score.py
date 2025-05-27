from django.db.models import Max
from rest_framework import serializers

from memorix.models import Category


def prepare_score_data(validated_data, context):
    """Prepare the score data for saving."""
    request = context.get('request')
    category_code = validated_data.pop('category')
    try:
        category = Category.objects.get(code=category_code.upper())
        validated_data['category'] = category
    except Category.DoesNotExist as err:
        raise serializers.ValidationError(
            {'category': f"Category '{category_code}' not found"}
        ) from err

    if request and hasattr(request, 'user') and request.user.is_authenticated:
        validated_data['profile'] = request.user.profile
    else:
        raise serializers.ValidationError(
            {'profile': 'Authenticated user is required to save the score.'}
        )

    return validated_data


def get_leaderboard_scores(category_id=None, limit=10):
    from memorix.models import Score

    queryset = Score.objects.all()
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    return queryset.order_by('-stars', 'time_seconds', 'moves')[:limit]


def get_user_best_scores(profile):
    from memorix.models import Score

    categories = (
        Score.objects.filter(profile=profile)
        .values_list('category', flat=True)
        .distinct()
    )
    best_scores = []
    for category_id in categories:
        max_stars = Score.objects.filter(
            profile=profile, category=category_id
        ).aggregate(Max('stars'))['stars__max']
        best_score = (
            Score.objects.filter(
                profile=profile, category=category_id, stars=max_stars
            )
            .order_by('moves', 'time_seconds')
            .first()
        )
        if best_score:
            best_scores.append(best_score)
    return best_scores
