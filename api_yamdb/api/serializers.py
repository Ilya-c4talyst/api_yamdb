import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import serializers

from reviews.models import Category, Genre, Title, GenreTitle


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
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
            # if Genre.objects.filter(slug=genre_slug).exists():
            #     genres.append(Genre.objects.get(slug=genre_slug))
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
