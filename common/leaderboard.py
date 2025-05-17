from collections import defaultdict

from memorix.models import Leaderboard, Score, Category


def update_category_leaderboard(category, top_count=5):
    """Update the leaderboard for a specific category."""

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
    """Get the top N leaderboard entries for each category."""
    queryset = Leaderboard.objects.select_related(
        'score', 'score__profile', 'score__profile__owner', 'category'
    )
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    queryset = queryset.order_by('category', 'rank')
    grouped = defaultdict(list)
    for entry in queryset:
        grouped[entry.category_id].append(entry)
    top_entries = []
    for entries in grouped.values():
        top_entries.extend(entries[:top_count])

    return top_entries

def update_leaderboard_async(category_id):
    """Update leaderboard for a category using its ID."""
    try:
        category = Category.objects.get(id=category_id)
        update_category_leaderboard(category)
    except Category.DoesNotExist:
        # Handle the error or log it
        pass
