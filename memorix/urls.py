from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ScoreViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'results', ScoreViewSet, basename='gameresult')

urlpatterns = [
    path('memorix/', include(router.urls)),
]
