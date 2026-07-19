from django_filters.rest_framework import FilterSet, filters

from .models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_carts=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author']


class IngredientFilter(FilterSet):
    name = filters.CharFilter(method='filter_name')

    def filter_name(self, queryset, name, value):
        if not value:
            return queryset

        starts = queryset.filter(name__istartswith=value)
        contains = queryset.filter(
            name__icontains=value
        ).exclude(name__istartswith=value)
        return starts.union(contains)

    class Meta:
        model = Ingredient
        fields = ('name',)
