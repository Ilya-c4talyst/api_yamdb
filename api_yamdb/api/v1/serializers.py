import datetime as dt
import uuid

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.models import User, Category, Genre, Title, GenreTitle, Comment, Review
from .validators import validate_email, validate_username


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)
    username = serializers.SlugField(read_only=True)
    email = serializers.SlugField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role', 'confirmation_code')
    
    def create(self, validated_data):
        email = validated_data['email']
        confirmation_code = str(uuid.uuid3(uuid.NAMESPACE_X500, email))
        return User.objects.create(
            **validated_data,
            confirmation_code=confirmation_code
        )
    
    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError()
        elif name is None or name == "":
            raise serializers.ValidationError()
        return name

    def validate_email(self, email):
        if email is None or email == "":
            raise serializers.ValidationError()
        return email


class UserAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role', 'confirmation_code')

    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError()
        elif name is None or name == "":
            raise serializers.ValidationError()
        return name

    def validate_email(self, email):
        if email is None or email == "":
            raise serializers.ValidationError()
        return email


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError()
        elif name is None or name == "":
            raise serializers.ValidationError()
        return name

    def validate_email(self, email):
        if email is None or email == "":
            raise serializers.ValidationError()
        return email


class GetTokenSerializer(serializers.Serializer):
    username = serializers.SlugField(required=True)
    confirmation_code = serializers.SlugField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
    
    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError()
        elif name is None or name == "":
            raise serializers.ValidationError()
        return name



class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        lookup_field = 'slug'
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class genre_type(serializers.Field):
    """Пользовательское поле для управления genre"""

    def to_representation(self, value):
        """Получаем объекты и переводим в json формат"""
        genres = GenreSerializer(value.all(), many=True)
        return genres.data

    def to_internal_value(self, data):
        """Запись"""
        genres = []
        for genre_slug in data:
            genres.append(get_object_or_404(Genre, slug=genre_slug))
        return genres


class category_type(serializers.Field):
    """Пользовательское поле для управления category"""

    def to_representation(self, value):
        """Получаем объекты и переводим в json формат"""
        category = GenreSerializer(value)
        return category.data

    def to_internal_value(self, data):
        """Запись"""
        return get_object_or_404(Category, slug=data)


class TitleSerializer(serializers.ModelSerializer):

    genre = genre_type()
    category = category_type()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')

    def get_rating(self, obj):
        return 5

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(
                genre=genre, title=title)
        return title

    def validate_year(self, value):
        year = dt.date.today().year
        if not (0 < value <= year):
            raise serializers.ValidationError('Не корректная дата! ')
        return value
    

class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='text')
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    
    class Meta:
        fields = "__all__"
        model = Review
    
    def validate(self, data):
        author = self.context['request'].user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(title=title_id, author=author).exists():
            raise ValidationError('Вы уже писали отзыв к этому произведению')
        return data
    
    def validate_score(self, value):
        if 0 > value > 10:
            raise ValidationError('Оценкой может быть число от 1 до 10')
        return value


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        read_only=True, slug_field='name')
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = "__all__"
        model = Comment