from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (Recipe, Tag, Ingredient, RecipeIngredient, ShoppingCart,
                     Subscription, Favorite,)


class RecipeCountAdminMixin:
    recipe_count_display = ('recipe_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipes'))

    @admin.display(description='Рецептов')
    def recipe_count(self, instance):
        return instance.recipe_count


class HasRelatedFilter(admin.SimpleListFilter):
    title = 'Есть'
    parameter_name = 'has_related'
    relation_field = None
    LOOKUPS = (
        ('yes', 'Да'),
        ('no', 'Нет'),
    )

    def lookups(self, request, model_admin):
        return self.LOOKUPS

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        lookup = {
            'yes': False,
            'no': True,
        }[self.value()]

        return queryset.filter(
            **{f'{self.relation_field}__isnull': lookup}
        ).distinct()


class UserHasRecipesFilter(HasRelatedFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    relation_field = 'recipes'


class UserHasSubscriptionsFilter(HasRelatedFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    relation_field = 'subscriptions'


class UserHasSubscribersFilter(HasRelatedFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'
    relation_field = 'author_subscriptions'


class IngredientHasRecipesFilter(HasRelatedFilter):
    title = 'Есть в рецептах'
    parameter_name = 'has_recipes'
    relation_field = 'recipes'


@admin.register(Ingredient)
class IngredientAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',
                    *RecipeCountAdminMixin.recipe_count_display,)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit', IngredientHasRecipesFilter,)


@admin.register(Tag)
class TagAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',
                    *RecipeCountAdminMixin.recipe_count_display,)
    search_fields = ('name',)
    readonly_fields = ('recipe_count',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)
    extra = 1
    min_num = 1
    readonly_fields = ('measurement_unit',)
    fields = ('ingredient', 'measurement_unit', 'amount')

    @admin.display(description='Ед. изм.')
    def measurement_unit(self, obj):
        if obj.ingredient:
            return obj.ingredient.measurement_unit
        return '-'


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_group'
    FAST_TIME = 30
    LONG_TIME = 60
    TIME_RANGES = {
        'fast': (0, FAST_TIME - 1),
        'medium': (FAST_TIME, LONG_TIME),
        'long': (LONG_TIME + 1, 10 ** 9),
    }

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)

        fast_count = recipes.filter(
            cooking_time__range=self.TIME_RANGES['fast']
        ).count()

        medium_count = recipes.filter(
            cooking_time__range=self.TIME_RANGES['medium']
        ).count()

        long_count = recipes.filter(
            cooking_time__range=self.TIME_RANGES['long']
        ).count()

        return (
            (
                'fast',
                f'Меньше {self.FAST_TIME} минут ({fast_count})'
            ),
            (
                'medium',
                f'От {self.FAST_TIME} до '
                f'{self.LONG_TIME} минут ({medium_count})'
            ),
            (
                'long',
                f'Дольше {self.LONG_TIME} минут ({long_count})'
            ),
        )

    def queryset(self, request, recipes):
        cooking_range = self.TIME_RANGES.get(self.value())

        if cooking_range:
            return recipes.filter(
                cooking_time__range=cooking_range
            )
        return recipes


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    fields = ('name', 'author', 'tags', 'text', 'cooking_time',
              ('image', 'image_preview'),)
    list_display = ('id', 'name', 'cooking_time_display', 'author',
                    'favorites_count', 'ingredients_list', 'tags_list',
                    'image_preview',)
    search_fields = ('name', 'author_first_name',
                     'author_last_name', 'author_username')
    list_filter = ('author', 'tags', CookingTimeFilter,)

    readonly_fields = ('favorites_count', 'image_preview',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                favorites_count=Count(
                    'favorites',
                    distinct=True,
                )
            )
            .prefetch_related(
                'recipe_ingredients__ingredient',
                'tags',
            )
        )

    @admin.display(description=mark_safe('Время<br>(мин)'))
    def cooking_time_display(self, obj):
        return obj.cooking_time

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe):
        return mark_safe(
            '<br>'.join(
                f'{item.ingredient.name} — '
                f'{item.amount} '
                f'{item.ingredient.measurement_unit}'
                for item in recipe.recipe_ingredients.all()))

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        return mark_safe(
            '<br>'.join(
                tag.name
                for tag in recipe.tags.all()))

    @admin.display(description='Картинка')
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" '
                'style="max-width:100px; max-height:100px;">'
            )
        return '-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)


class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeRelationAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeRelationAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


@admin.register(get_user_model())
class UserAdminConfig(RecipeCountAdminMixin, UserAdmin):
    list_display = ('id', 'username', 'full_name', 'email', 'avatar_preview',
                    'recipe_count', 'subscriptions_count',
                    'subscribers_count',)
    list_filter = (UserHasRecipesFilter, UserHasSubscriptionsFilter,
                   UserHasSubscribersFilter,)

    search_fields = ('username', 'email', 'first_name', 'last_name',)

    readonly_fields = ('avatar_preview', 'recipe_count', 'subscriptions_count',
                       'subscribers_count',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'Дополнительно',
            {
                'fields': (
                    'avatar',
                    'avatar_preview',
                    'recipe_count',
                    'subscriptions_count',
                    'subscribers_count',
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                subscriptions_count=Count('subscriptions', distinct=True),
                subscribers_count=Count('author_subscriptions', distinct=True),
            )
        )

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'.strip()

    @admin.display(description='Аватар')
    def avatar_preview(self, user):
        if not user.avatar:
            return '—'
        return mark_safe(
            f'<img src="{user.avatar.url}" '
            'width="50" height="50" '
            'style="border-radius:50%;">'
        )

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscriptions_count

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.subscribers_count


admin.site.unregister(Group)
