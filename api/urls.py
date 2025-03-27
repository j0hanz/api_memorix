"""URL configuration"""

from django.contrib import admin
from django.urls import include, path

from .views import RootRoute

urlpatterns = [
    path('', RootRoute.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
]
