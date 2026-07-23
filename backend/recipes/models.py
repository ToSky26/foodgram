from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import (
    RECIPE_NAME_LENGTH,
    TAG_NAME_SLUG_LENGTH,
    INGREDIENT_NAME_LENGTH,
    INGREDIENT_MEASUREMENT_LENGTH,
    MINIMUM_RECIPE_COOKING_TIME,
    MINIMUM_INGREDIENT_AMOUNT,
    MAX_EMAIL_LENGTH,
    MAX_USENAMES_LENGTH,
    USERNAME_REGEX
)


username_validator = RegexValidator(
    regex=USERNAME_REGEX,
    message=(
        'Имя пользователя может содержать только буквы, цифры '
        'и символы @/./+/-/_.'
    ),
)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        max_length=MAX_USENAMES_LENGTH,
        unique=True,
        validators=(username_validator,),
        verbose_name='Ник',
    )

    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name='Электронная почта',
    )

    first_name = models.CharField(
        max_length=MAX_USENAMES_LENGTH,
        verbose_name='Имя',
    )

    last_name = models.CharField(
        max_length=MAX_USENAMES_LENGTH,
        verbose_name='Фамилия',
    )

    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        verbose_name='Аватар',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=TAG_NAME_SLUG_LENGTH,
        verbose_name='Имя'
    )
    slug = models.SlugField(
        unique=True,
        max_length=TAG_NAME_SLUG_LENGTH,
        verbose_name='Идентификатор'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_LENGTH,
        verbose_name='Имя'
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_LENGTH,
        verbose_name='Имя'
    )
    text = models.TextField(verbose_name='Текст рецепта')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MINIMUM_RECIPE_COOKING_TIME)],
        verbose_name='Время готовки'
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MINIMUM_INGREDIENT_AMOUNT)],
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique',
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'


class Subscription(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='author_subscriptions',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscription',
            ),
        )
