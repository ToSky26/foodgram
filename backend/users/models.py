from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from .constants import (
    MAX_EMAIL_LENGTH,
    MAX_USENAMES_LENGTH
)


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=MAX_USENAMES_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_USENAMES_LENGTH,
        verbose_name='Фамилия'
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        through='recipes.Favorite',
        related_name='favorited_by',
        blank=True,
        verbose_name='Избранное'
    )

    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        through='recipes.ShoppingCart',
        related_name='in_carts',
        blank=True,
        verbose_name='В списке покупок'
    )

    subscriptions = models.ManyToManyField(
        'self',
        through='users.Subscription',
        symmetrical=False,
        related_name='subscribers',
        blank=True,
        verbose_name='Подписки'
    )

    avatar = models.ImageField(
        blank=True,
        upload_to='users/',
        verbose_name='Аватар'
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('author')),
                name='no_self_subscription'
            )
        ]
