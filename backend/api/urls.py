from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.viewsets import UserViewSet
from .viewsets import RecipeViewSet, TagViewSet, IngredientViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
