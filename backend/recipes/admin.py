from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import Recipe, Tag, Ingredient, RecipeIngredient


class RecipeCountAdminMixin:
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipes')
        )

    @admin.display(description='Рецептов')
    def recipe_count(self, instance):
        return instance.recipe_count


@admin.register(Ingredient)
class IngredientAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count')
    search_fields = ('name',)
    readonly_fields = ('recipe_count',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)
    extra = 1
    min_num = 1


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_group'

    def lookups(self, request, model_admin):
        return (
            ('fast', 'До 30 минут'),
            ('medium', 'От 30 до 60 минут'),
            ('long', 'Дольше 60 минут'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lt=30)

        if self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=30,
                cooking_time__lte=60
            )

        if self.value() == 'long':
            return queryset.filter(cooking_time__gt=60)
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('id', 'name', 'cooking_time', 'author', 'favorites_count',
                    'ingredients_list', 'tags_list', 'image_preview',)
    search_fields = ('name', 'author_first_name',
                     'author_last_name', 'author_username')
    list_filter = ('author', 'tags', CookingTimeFilter,)

    readonly_fields = ('favorites_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorited_by')
        )

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorited_by.count

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, obj):
        return ', '.join(ingredient.name 
                         for ingredient in obj.ingredients.all())

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='Картинка')
    def image_preview(self, obj):
        return obj.image.url if obj.image else '-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(get_user_model())
class UserAdminConfig(UserAdmin):
    list_display = ('id', 'username', 'full_name', 'email', 'avatar_preview',
                    'recipe_count', 'subscriptions_count',
                    'subscribers_count',)

    search_fields = ('username', 'email', 'first_name', 'last_name',)

    readonly_fields = ('avatar_preview', 'recipe_count', 'subscriptions_count',
                       'subscribers_count',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                recipe_count=Count('recipes', distinct=True),
                subscriptions_count=Count('subscriptions', distinct=True),
                subscribers_count=Count('subscribers', distinct=True),
            )
        )

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'.strip()

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_preview(self, user):
        if not user.avatar:
            return '—'
        return (
            f'<img src="{user.avatar.url}" '
            'width="50" height="50" '
            'style="border-radius:50%;">'
        )

    @admin.display(description='Рецептов')
    def recipe_count(self, user):
        return user.recipe_count

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscriptions_count

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.subscribers_count


admin.site.unregister(Group)
