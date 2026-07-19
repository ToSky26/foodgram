from django.contrib import admin
from django.db.models import Count

from .models import Recipe, Tag, Ingredient, RecipeIngredient

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ('name',)
    readonly_fields = ('recipe_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipes')
        )

    @admin.display(description='Рецептов c этим ингредиентом')
    def recipe_count(self, obj):
        return obj.recipe_count

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count')
    search_fields = ('name',)
    readonly_fields = ('recipe_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipes')
        )

    @admin.display(description='Рецептов с этим тегом')
    def recipe_count(self, obj):
        return obj.recipe_count


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)
    extra = 1
    min_num = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author__first_name')
    search_fields = ('name', 'author__first_name',
                     'author__last_name', 'author__username')
    list_filter = ('tags',)

    readonly_fields = ('favorites_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorited_by')
        )

    @admin.display(description='В избранном у')
    def favorites_count(self, obj):
        return obj.favorites.count


admin.site.register(RecipeIngredient)
