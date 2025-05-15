from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, LeaderboardViewSet, ScoreViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'results', ScoreViewSet, basename='gameresult')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('memorix/', include(router.urls)),
]
