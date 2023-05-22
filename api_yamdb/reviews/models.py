from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import custom_username_validator
from api_yamdb.settings import LENGTH_USERNAME, LENGTH_256


class User(AbstractUser):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    ROLES = [(USER, "user"), (ADMIN, "admin"), (MODERATOR, "moderator")]
    username = models.SlugField(
        max_length=LENGTH_USERNAME,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            custom_username_validator
        ]
    )
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, max_length=100, null=True)
    role = models.SlugField(choices=ROLES, default=USER, max_length=30)
    confirmation_code = models.SlugField(
        null=True, blank=True, max_length=200, editable=True, unique=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=LENGTH_256)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return f"{self.name}{self.slug}"


class Category(models.Model):
    name = models.CharField(max_length=LENGTH_256)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return f"{self.name}{self.slug}"


class Title(models.Model):
    name = models.CharField(max_length=LENGTH_256)
    year = models.SmallIntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre, through="GenreTitle", related_name="title", blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name="title", blank=True, null=True
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="произведение",
    )
    text = models.TextField(verbose_name="текст отзыва")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="review", verbose_name="автор"
    )
    score = models.IntegerField(
        verbose_name="оценка", validators=(MinValueValidator(1),
                                           MaxValueValidator(10))
    )
    pub_date = models.DateTimeField(verbose_name="дата публикации",
                                    auto_now_add=True)

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзыв"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "title",
                    "author",
                ),
                name="unique review",
            )
        ]
        ordering = ("pub_date",)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name="comment",
        verbose_name="отзыв"
    )
    text = models.TextField(verbose_name="текст комментария")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comment",
        verbose_name="автор"
    )
    pub_date = models.DateTimeField(verbose_name="дата публикации",
                                    auto_now_add=True)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарий"

    def __str__(self):
        return self.text
