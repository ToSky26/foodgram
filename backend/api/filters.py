from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(
    filters.FilterSet
):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(
    filters.FilterSet
):
    author = filters.NumberFilter(
        field_name='author__id'
    )

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = filters.NumberFilter(
        method='filter_favorited'
    )

    is_in_shopping_cart = filters.NumberFilter(
        method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
        )

    def filter_favorited(
        self,
        queryset,
        name,
        value
    ):
        user = self.request.user

        if user.is_anonymous:
            return queryset

        if value == 1:
            return queryset.filter(
                favorited_by__user=user
            )

        return queryset

    def filter_shopping_cart(
        self,
        queryset,
        name,
        value
    ):
        user = self.request.user

        if user.is_anonymous:
            return queryset

        if value == 1:
            return queryset.filter(
                in_carts__user=user
            )

        return queryset
