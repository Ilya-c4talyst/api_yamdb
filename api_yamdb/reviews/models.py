from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


user = 'user'
moderator = 'moderator'
admin = 'admin'

CHOICES = [
    (user, 'user'),
    (moderator, 'moderator'),
    (admin, 'admin'),
]


class User(AbstractUser):
    username = models.SlugField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, max_length=254)
    role = models.SlugField(choices=CHOICES, default=user)
    bio = models.TextField(blank=True)
    confirmation_code = models.SlugField(null=True, blank=True)


    @property
    def is_user(self):
        return self.role == user
    
    @property
    def is_moderator(self):
        return self.role == moderator
    
    @property
    def is_admin(self):
        return self.role == admin

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Title(models.Model):
    pass


class Genre(models.Model):
    pass


class Review(models.Model):
    """Модель отзыва + рейтинг."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                               related_name='review',
                               verbose_name='произведение')
    text = models.TextField(verbose_name='текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='review',
                               verbose_name='автор')
    score = models.IntegerField(verbose_name='оценка',
                                validators=(MinValueValidator(1),MaxValueValidator(10))
                                )
    pub_date = models.DateTimeField(verbose_name='дата публикации',
                                    auto_now_add=True)
    
    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзыв'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review')
                ]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comment',
                               verbose_name='отзыв')
    text = models.TextField(verbose_name='текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comment',
                               verbose_name='автор')
    pub_date = models.DateTimeField(verbose_name='дата публикации',
                                    auto_now_add=True)
    
    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарий'

    def __str__(self):
        return self.text
