import uuid

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from .pagination import UserPagination
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User, Genre, Category, Title, Review, Comment
from api_yamdb.settings import ADMIN_EMAIL
from .permissions import IsAdmin, IsAuthorModeratorAdminOrReadOnly, ReadOnly
from .serializers import GetTokenSerializer,SignUpSerializer,UserAdminSerializer, UserSerializer, GenreSerializer, CategorySerializer, TitleSerializer, ReviewSerializer, CommentSerializer


class ListCreateDeleteViewSet(
        mixins.ListModelMixin, mixins.CreateModelMixin,
        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ('name',)
    
    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return (IsAdmin(),)


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ('name',)
    
    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return (IsAdmin(),)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return (IsAdmin(),)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdmin,)
    pagination_class = UserPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username',)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        pagination_class=[UserPagination],
        url_path='me',
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )


@api_view(['POST'])
def signup(request):
    user = User.objects.filter(**request.data)
    if user.exists():
        get_and_send_confirmation_code(user)
        return Response(request.data, status=status.HTTP_200_OK)

    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        user = User.objects.filter(**serializer.data)
        get_and_send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
def token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=serializer.data['username'])
    if serializer.data['confirmation_code'] == user.confirmation_code:
        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
    return Response(
        status=status.HTTP_400_BAD_REQUEST
    )


def get_and_send_confirmation_code(user):
    for u in user:
        u.confirmation_code = str(uuid.uuid4()).split("-")[0]
        u.save()
        send_mail(
            'Код подтверждения',
            f'Код подтверждения "{u.username}": {u.confirmation_code}',
            ADMIN_EMAIL,
            [u.email]
        )



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return (IsAuthorModeratorAdminOrReadOnly(),)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return (IsAuthorModeratorAdminOrReadOnly(),)