from django.contrib import admin

from reviews.models import (Category, Comment, Genre,
                            GenreTitle, Review, Title, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "first_name",
                    "last_name", "email", "role", "bio")
    list_editable = ("role",)
    search_fields = ("username",)
    empty_value_display = "-empty-"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = "-пусто-"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = "-пусто-"


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "category")
    list_editable = ("category",)
    search_fields = (
        "name",
        "year",
    )
    empty_value_display = "-пусто-"


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ("title", "genre")
    list_editable = ("genre",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "text",
        "author",
        "score",
        "pub_date",
    )
    search_fields = ("text", "score", "author")
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "review",
        "text",
        "author",
        "pub_date",
    )
    search_fields = (
        "text",
        "author",
    )
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"
