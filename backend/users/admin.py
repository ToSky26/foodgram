from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )

    search_fields = (
        'email',
        'username',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', )
    search_fields = ('user_email', 'author_email', )
