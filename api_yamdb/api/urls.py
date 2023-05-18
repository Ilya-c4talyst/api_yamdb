from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                          ReviewViewSet, TitleViewSet, UserViewSet, signup,
                          token)

router_v1 = DefaultRouter()

router_v1.register("categories", CategoryViewSet, basename="categories")
router_v1.register("genres", GenreViewSet, basename="genres")
router_v1.register("titles", TitleViewSet, basename="titles")
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)
router_v1.register(r"users", UserViewSet)
auth_patterns = [
    path("auth/token/", token, name="token"),
    path("auth/signup/", signup, name="signup"),
]

urlpatterns = [
    path("v1/", include(auth_patterns)),
    path("v1/", include(router_v1.urls)),
]
