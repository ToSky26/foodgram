from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.viewsets import RecipeViewSet, TagViewSet, IngredientViewSet


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
