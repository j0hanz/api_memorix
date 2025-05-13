from common.score import get_leaderboard_scores, get_user_best_scores
from memorix.models import Score


def get_user_scores_queryset(request):
    user = request.user
    if not user.is_authenticated:
        return Score.objects.none()
    profile = getattr(user, 'profile', None)
    queryset = (
        Score.objects.filter(profile=profile)
        if profile
        else Score.objects.none()
    )
    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(category__code=category.upper())
    return queryset


def get_leaderboard_data(request, serializer_class):
    category_id = request.query_params.get('category')
    top_results = get_leaderboard_scores(category_id)
    serializer = serializer_class(
        top_results, many=True, context={'request': request}
    )
    return serializer.data


def get_best_scores_data(request, serializer_class):
    user = request.user
    profile = getattr(user, 'profile', None)
    if not user.is_authenticated or not profile:
        return []
    best_scores = get_user_best_scores(profile)
    serializer = serializer_class(
        best_scores, many=True, context={'request': request}
    )
    return serializer.data
