from collections import defaultdict

from memorix.models import Category, Leaderboard, Score


def update_category_leaderboard(category, top_count=5):
    """Update the leaderboard for a specific category."""
    top_scores = Score.objects.filter(category=category).order_by(
        '-stars', 'time_seconds', 'moves'
    )[:top_count]
    existing_entries = Leaderboard.objects.filter(category=category)
    existing_entries.delete()
    leaderboard_entries = []
    for rank, score in enumerate(top_scores, 1):
        leaderboard_entries.append(
            Leaderboard(score=score, category=category, rank=rank)
        )
    if leaderboard_entries:
        Leaderboard.objects.bulk_create(leaderboard_entries)


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
