from django.contrib import admin

from .models import User, Review, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'first_name', 'last_name', 'email', 'role', 'bio'
    )
    list_editable = ('role',)
    search_fields = ('username',)
    empty_value_display = '-empty-'

admin.site.register(Review)
admin.site.register(Comment)