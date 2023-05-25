import datetime as dt

from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers

from reviews.models import (Category, Comment, Genre, Review,
                            Title, User)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def create(self, validated_data):
        confirmation_code = default_token_generator.make_token(
            validated_data["user"]
        )
        return User.objects.create(
            **validated_data, confirmation_code=confirmation_code
        )


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")


class GetTokenSerializer(serializers.Serializer):
    username = serializers.SlugField(required=True)
    confirmation_code = serializers.SlugField(required=True)

    def validate_username(self, name):
        if name == "me":
            raise serializers.ValidationError()
        return name


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username")

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review

    def validate(self, data):
        if self.context["request"].method != "POST":
            return data
        author = self.context["request"].user
        title_id = self.context.get("view").kwargs.get("title_id")
        if Review.objects.filter(title=title_id, author=author).exists():
            raise serializers.ValidationError(
                "Вы уже писали отзыв к этому произведению"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field="username")

    class Meta:
        fields = fields = ("id", "text", "author", "pub_date")
        model = Comment


class TitleSerializer(serializers.ModelSerializer):

    genre = serializers.PrimaryKeyRelatedField(many=True,
                                               queryset=Genre.objects.all())
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return self.context['view'].queryset.get(id=obj.id).rating

    class Meta:
        model = Title
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError("Не корректная дата! ")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        category = rep.get('category')
        if category:
            catogeory_ob = Category.objects.get(pk=category)
            rep['category'] = CategorySerializer(catogeory_ob).data
        list_genre_ob = []
        for genre in rep.get('genre'):
            list_genre_ob.append(Genre.objects.get(pk=genre))
        rep['genre'] = GenreSerializer(list_genre_ob, many=True).data
        return rep
