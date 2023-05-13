from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .v1.views import (signup, token)

v1_router = DefaultRouter()


auth_patterns = [
    path('auth/token/', token, name='token'),
    path('auth/signup/', signup, name='signup')
]

urlpatterns = [
    path('v1/', include(auth_patterns))
]
