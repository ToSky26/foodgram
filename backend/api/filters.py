from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag, Ingredient


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

    def filter_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(shoppingcarts__user=self.request.user)
        return recipes

    class Meta:
        model = Recipe
        fields = ['author']


class IngredientFilter(FilterSet):
    name = filters.CharFilter(method='filter_name')

    def filter_name(self, ingredients, name, value):
        if not value:
            return ingredients

        starts = ingredients.filter(name__istartswith=value)
        contains = ingredients.filter(
            name__icontains=value
        ).exclude(name__istartswith=value)
        return starts.union(contains)

    class Meta:
        model = Ingredient
        fields = ('name',)
