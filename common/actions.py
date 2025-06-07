from rest_framework import status
from rest_framework.response import Response

from common.utils import get_best_scores_data


class ScoreActionMixin:
    """Mixin providing score-related action handlers."""

    def handle_best_scores(self, request):
        """Get user's best scores across all categories."""
        data = get_best_scores_data(request, self.get_serializer_class())
        return Response(data)

    def handle_recent_scores(self, request):
        """Get user's most recent game scores."""
        queryset = self.get_queryset().order_by('-completed_at')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def handle_scores_by_category(self, request, category_code=None):
        """Get user's scores for a specific category."""
        category = self.get_category_or_404(category_code)
        if not category:
            return Response(
                {'detail': 'Category not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = self.filter_queryset(
            self.get_queryset().filter(category=category)
        )
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def handle_clear_category_scores(self, request, category_code=None):
        """Clear all user's scores for a specific category."""
        category = self.get_category_or_404(category_code)
        if not category:
            return Response(
                {'detail': 'Category not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        scores_to_delete = self.get_queryset().filter(category=category)
        deleted_count = scores_to_delete.count()

        if deleted_count == 0:
            return Response(
                {'detail': 'No scores found for this category.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        scores_to_delete.delete()
        from common.leaderboard import update_category_leaderboard

        update_category_leaderboard(category)

        return Response(
            {
                'detail': f'Successfully deleted {deleted_count} scores for'
                f' {category.name}.'
            },
            status=status.HTTP_200_OK,
        )

    def handle_clear_all_scores(self, request):
        """Clear all user's scores across all categories."""
        scores_to_delete = self.get_queryset()
        deleted_count = scores_to_delete.count()

        if deleted_count == 0:
            return Response(
                {'detail': 'No scores found to delete.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        categories = set(
            scores_to_delete.values_list('category_id', flat=True)
        )
        scores_to_delete.delete()

        from common.leaderboard import update_category_leaderboard
        from memorix.models import Category

        for category_id in categories:
            try:
                category = Category.objects.get(id=category_id)
                update_category_leaderboard(category)
            except Category.DoesNotExist:
                pass

        return Response(
            {'detail': f'Successfully deleted all {deleted_count} scores.'},
            status=status.HTTP_200_OK,
        )


class LeaderboardActionMixin:
    """Mixin providing leaderboard-related action handlers."""

    def handle_top_players(self, request, limit=None):
        """Get top N players across all categories."""
        try:
            limit = min(int(limit), 100)
        except (ValueError, TypeError):
            limit = 10

        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def handle_user_rank(self, request):
        """Get user's rankings across all categories."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_ranks = []
        user_profile = getattr(request.user, 'profile', None)

        if user_profile:
            from memorix.models import Category, Leaderboard

            for category in Category.objects.all():
                try:
                    leaderboard_entry = Leaderboard.objects.get(
                        score__profile=user_profile, category=category
                    )
                    user_ranks.append(
                        {
                            'category': category.name,
                            'category_code': category.code,
                            'rank': leaderboard_entry.rank,
                            'score_id': leaderboard_entry.score.id,
                        }
                    )
                except Leaderboard.DoesNotExist:
                    continue

        return Response(
            {'username': request.user.username, 'rankings': user_ranks}
        )

    def handle_category_top(self, request, category_code=None, limit=None):
        """Get top players for a specific category."""
        from memorix.models import Category, Leaderboard

        try:
            category = Category.objects.get(code=category_code.upper())
            limit = min(int(limit), 50)
        except (ValueError, TypeError):
            limit = 10
        except Category.DoesNotExist:
            return Response(
                {'detail': 'Category not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = (
            Leaderboard.objects.filter(category=category)
            .select_related('score', 'score__profile', 'score__profile__owner')
            .order_by('rank')[:limit]
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'category': category.name,
                'category_code': category.code,
                'leaderboard': serializer.data,
            }
        )


class GameActionMixin(ScoreActionMixin, LeaderboardActionMixin):
    """Mixin providing game-related action handlers."""


def get_best_scores_action(viewset_instance, request):
    """Standalone function for getting user's best scores."""
    data = get_best_scores_data(
        request, viewset_instance.get_serializer_class()
    )
    return Response(data)


def get_recent_scores_action(viewset_instance, request):
    """Standalone function for getting user's recent scores."""
    queryset = viewset_instance.get_queryset().order_by('-completed_at')[:10]
    serializer = viewset_instance.get_serializer(queryset, many=True)
    return Response(serializer.data)


def get_scores_by_category_action(
    viewset_instance, request, category_code=None
):
    """Standalone function for getting scores by category."""
    category = viewset_instance.get_category_or_404(category_code)
    if not category:
        return Response(
            {'detail': 'Category not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    queryset = viewset_instance.filter_queryset(
        viewset_instance.get_queryset().filter(category=category)
    )
    page = viewset_instance.paginate_queryset(queryset)

    if page is not None:
        serializer = viewset_instance.get_serializer(page, many=True)
        return viewset_instance.get_paginated_response(serializer.data)

    serializer = viewset_instance.get_serializer(queryset, many=True)
    return Response(serializer.data)


def clear_category_scores_action(
    viewset_instance, request, category_code=None
):
    """Standalone function for clearing category scores."""
    category = viewset_instance.get_category_or_404(category_code)
    if not category:
        return Response(
            {'detail': 'Category not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    scores_to_delete = viewset_instance.get_queryset().filter(
        category=category
    )
    deleted_count = scores_to_delete.count()

    if deleted_count == 0:
        return Response(
            {'detail': 'No scores found for this category.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    scores_to_delete.delete()
    from common.leaderboard import update_category_leaderboard

    update_category_leaderboard(category)

    return Response(
        {
            'detail': f'Successfully deleted {deleted_count} scores for'
            f' {category.name}.'
        },
        status=status.HTTP_200_OK,
    )


def clear_all_scores_action(viewset_instance, request):
    """Standalone function for clearing all scores."""
    scores_to_delete = viewset_instance.get_queryset()
    deleted_count = scores_to_delete.count()

    if deleted_count == 0:
        return Response(
            {'detail': 'No scores found to delete.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    categories = set(scores_to_delete.values_list('category_id', flat=True))
    scores_to_delete.delete()

    # Update leaderboards directly
    from common.leaderboard import update_category_leaderboard
    from memorix.models import Category

    for category_id in categories:
        try:
            category = Category.objects.get(id=category_id)
            update_category_leaderboard(category)
        except Category.DoesNotExist:
            pass

    return Response(
        {'detail': f'Successfully deleted all {deleted_count} scores.'},
        status=status.HTTP_200_OK,
    )


def get_top_players_action(viewset_instance, request, limit=None):
    """Standalone function for getting top players."""
    try:
        limit = min(int(limit), 100)
    except (ValueError, TypeError):
        limit = 10

    queryset = viewset_instance.get_queryset()[:limit]
    serializer = viewset_instance.get_serializer(queryset, many=True)
    return Response(serializer.data)


def get_user_rank_action(viewset_instance, request):
    """Standalone function for getting user's rank."""
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Authentication required.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user_ranks = []
    user_profile = getattr(request.user, 'profile', None)

    if user_profile:
        from memorix.models import Category, Leaderboard

        for category in Category.objects.all():
            try:
                leaderboard_entry = Leaderboard.objects.get(
                    score__profile=user_profile, category=category
                )
                user_ranks.append(
                    {
                        'category': category.name,
                        'category_code': category.code,
                        'rank': leaderboard_entry.rank,
                        'score_id': leaderboard_entry.score.id,
                    }
                )
            except Leaderboard.DoesNotExist:
                continue

    return Response(
        {'username': request.user.username, 'rankings': user_ranks}
    )


def get_category_top_action(
    viewset_instance, request, category_code=None, limit=None
):
    """Standalone function for getting category top players."""
    from memorix.models import Category, Leaderboard

    try:
        category = Category.objects.get(code=category_code.upper())
        limit = min(int(limit), 50)
    except (ValueError, TypeError):
        limit = 10
    except Category.DoesNotExist:
        return Response(
            {'detail': 'Category not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    queryset = (
        Leaderboard.objects.filter(category=category)
        .select_related('score', 'score__profile', 'score__profile__owner')
        .order_by('rank')[:limit]
    )

    serializer = viewset_instance.get_serializer(queryset, many=True)
    return Response(
        {
            'category': category.name,
            'category_code': category.code,
            'leaderboard': serializer.data,
        }
    )
