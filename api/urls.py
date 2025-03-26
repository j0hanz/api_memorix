"""URL configuration"""

from django.contrib import admin
from django.urls import path

from .views import RootRoute

urlpatterns = [
    path('', RootRoute.as_view()),
    path('admin/', admin.site.urls),
]
