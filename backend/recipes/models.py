import secrets

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    RECIPE_NAME_LENGTH,
    TAG_NAME_SLUG_LENGTH,
    INGREDIENT_NAME_LENGTH,
    INGREDIENT_MEASUREMENT_LENGTH,
    SHORTLINK_LENGTH,
    MINIMUM_RECIPE_COOKING_TIME,
    MINIMUM_INGREDIENT_AMOUNT,
)


class Tag(models.Model):
    name = models.CharField(
        unique=True, 
        max_length=TAG_NAME_SLUG_LENGTH,
        verbose_name='Имя тега'
    )
    slug = models.SlugField(
        unique=True,
        max_length=TAG_NAME_SLUG_LENGTH,
        verbose_name='Slug тега'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_LENGTH,
        verbose_name='Имя ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        verbose_name='Имя рецепта'
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
        verbose_name='Автор рецепта'
    )
    short_link = models.CharField(
        max_length=SHORTLINK_LENGTH,
        unique=True,
        blank=True,
        verbose_name='Короткая ссылка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_link:
            while True:
                short_link = secrets.token_urlsafe(4)
                if not Recipe.objects.filter(short_link=short_link).exists():
                    self.short_link = short_link
                    break
        return (super().save(*args, **kwargs))


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


class Favorite(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
