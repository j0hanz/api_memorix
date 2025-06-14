"""URL configuration"""

from django.contrib import admin
from django.urls import include, path

from .views import LogoutView, RootRoute

urlpatterns = [
    path('', RootRoute.as_view()),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path(
        'dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')
    ),
    path('dj-rest-auth/logout/', LogoutView.as_view(), name='custom_logout'),
    path('api/', include('users.urls')),
    path('api/', include('memorix.urls')),
]
