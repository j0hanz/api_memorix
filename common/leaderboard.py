def update_category_leaderboard(category, top_count=5):
    """Update the leaderboard for a specific category."""
    from memorix.models import Leaderboard, Score

    top_scores = Score.objects.filter(category=category).order_by(
        '-stars', 'time_seconds', 'moves'
    )[:top_count]
    existing_entries = Leaderboard.objects.filter(category=category)
    top_score_ids = [score.id for score in top_scores]
    entries_to_remove = existing_entries.exclude(score_id__in=top_score_ids)
    entries_to_remove.delete()
    for rank, score in enumerate(top_scores, 1):
        Leaderboard.objects.update_or_create(
            score=score, category=category, defaults={'rank': rank}
        )


def get_category_leaderboard(category_id=None, top_count=5):
    """Get the leaderboard for a specific category or all categories."""
    from memorix.models import Leaderboard

    queryset = Leaderboard.objects.select_related(
        'score', 'score__profile', 'score__profile__owner', 'category'
    )
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    return queryset.order_by('category', 'rank')
