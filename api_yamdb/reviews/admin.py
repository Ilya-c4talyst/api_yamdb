from django.contrib import admin

from reviews.models import Comment, Review


admin.site.register(Review)
admin.site.register(Comment)