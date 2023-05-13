from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, primary_key=True)

    def __str__(self):
        return f'{self.name} {self.slug}'


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, primary_key=True)

    def __str__(self):
        return f'{self.name} {self.slug}'


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(null=True)
    genre = models.ManyToManyField(
        Genre, through='GenreTitle', related_name='title', blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='title', blank=True, null=True
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
