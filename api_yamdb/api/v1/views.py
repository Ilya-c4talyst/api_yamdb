from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


from api.v1.permissions import (
    IsAdmin,
    IsAuthorModeratorAdminOrReadOnly,
    ReadOnlyOrAdmin,
)
from api.v1.serializers import (
    GetTokenSerializer,
    SignUpSerializer,
    UserAdminSerializer,
    UserSerializer,
    GenreSerializer,
    CategorySerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from api.v1.utils import get_and_send_confirmation_code
from reviews.models import Category, Genre, Review, Title, User


class ListCreateDeleteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    search_fields = ("name",)
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.action == "list":
            return (ReadOnlyOrAdmin(),)
        return (IsAdmin(),)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("year", "name")
    search_fields = ("genre__slug",)
    permission_classes = (ReadOnlyOrAdmin,)
    http_method_names = ["patch", "get", "post", "delete"]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleWriteSerializer
        else:
            return TitleReadSerializer

    def get_queryset(self):
        queryset = Title.objects.annotate(rating=Avg('review__score'))
        genre_slug = self.request.query_params.get("genre")
        category_slug = self.request.query_params.get("category")
        if genre_slug is not None:
            queryset = queryset.filter(genre=genre_slug)
        if category_slug is not None:
            queryset = queryset.filter(category=category_slug)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ["patch", "get", "post", "delete"]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == "GET":
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def signup(request):
    user = User.objects.filter(
        username=request.data.get("username"), email=request.data.get("email")
    )
    if user.exists():
        get_and_send_confirmation_code(user)
        return Response(request.data, status=status.HTTP_200_OK)

    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        user = User.objects.filter(**serializer.data)
        get_and_send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=serializer.data["username"])

    if serializer.data["confirmation_code"] == user.confirmation_code:
        access_token = AccessToken.for_user(user)
        return Response(
            {"access_token": str(access_token)}, status=status.HTTP_200_OK
        )

    return Response(status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    http_method_names = ["patch", "get", "post", "delete"]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs["title_id"])
        return title.review.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs["title_id"])
        serializer.save(author=self.request.user, title=title)

    def perform_update(self, serializer):
        review = self.get_object()
        if not (
            self.request.user == review.author
            or self.request.user.is_staff
            or self.request.user.is_moderator
            or self.request.user.is_admin
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        review = get_object_or_404(
            Review, pk=self.kwargs["review_id"], title=self.kwargs["title_id"]
        )
        return review.comment.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, pk=self.kwargs["review_id"], title=self.kwargs["title_id"]
        )
        serializer.save(author=self.request.user, review=review)

    def perform_update(self, serializer):
        comment = self.get_object()
        if not (
            self.request.user == comment.author
            or self.request.user.is_staff
            or self.request.user.is_moderator
            or self.request.user.is_admin
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
