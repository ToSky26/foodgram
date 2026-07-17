from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

from users.views import FoodgramUserViewSet

router = DefaultRouter()

router.register(
    'users',
    FoodgramUserViewSet,
    basename='users'
)

router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)

router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

router.register(
    'tags',
    TagViewSet,
    basename='tags'
)

urlpatterns = [
    path('', include(router.urls)),
]
