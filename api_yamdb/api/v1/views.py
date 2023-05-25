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
    TitleSerializer,
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
    permission_classes = (ReadOnlyOrAdmin,)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("year", "name", "genre", "category")
    search_fields = ("genre__slug",)
    permission_classes = (ReadOnlyOrAdmin,)
    http_method_names = ["patch", "get", "post", "delete"]
    serializer_class = TitleSerializer
    queryset = Title.objects.annotate(rating=Avg('review__score')).all()


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
    serializer.is_valid(raise_exception=True)
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
            {"token": str(access_token)}, status=status.HTTP_200_OK
        )

    return Response(status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    http_method_names = ["patch", "get", "post", "delete"]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs["title_id"])

    def get_queryset(self):
        return self.get_title().review.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    http_method_names = ["patch", "get", "post", "delete"]

    def get_review(self):
        return get_object_or_404(
            Review, pk=self.kwargs["review_id"], title=self.kwargs["title_id"]
        )

    def get_queryset(self):
        return self.get_review().comment.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
