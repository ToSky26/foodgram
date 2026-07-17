from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Recipe, ShoppingCart
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.api.serializers.recipe_serializers import (RecipeReadSerializer,
                                                        RecipeShortSerializer,
                                                        RecipeWriteSerializer)


class RecipeViewSet(ModelViewSet):
    permission_classes = (
        IsAuthorOrReadOnly,
    )

    filterset_class = RecipeFilter

    def get_queryset(self):
        return (
            Recipe.objects
            .select_related('author')
            .prefetch_related(
                'tags',
                'recipe_ingredients__ingredient',
            )
            .order_by('-id')
        )

    def get_serializer_class(self):
        if self.action in (
            'create',
            'update',
            'partial_update',
        ):
            return RecipeWriteSerializer

        return RecipeReadSerializer

    def add_relation(
        self,
        request,
        pk,
        model,
    ):
        recipe = get_object_or_404(
            Recipe,
            pk=pk,
        )

        if model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).exists():
            return Response(
                {
                    'errors': 'Рецепт уже добавлен.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        model.objects.create(
            user=request.user,
            recipe=recipe,
        )

        return Response(
            RecipeShortSerializer(
                recipe,
                context={
                    'request': request
                }
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            IsAuthenticated
        ],
    )
    def favorite(
        self,
        request,
        pk=None,
    ):
        return self.add_relation(
            request,
            pk,
            Favorite,
        )

    @favorite.mapping.delete
    def delete_favorite(
        self,
        request,
        pk=None,
    ):
        favorite = Favorite.objects.filter(
            user=request.user,
            recipe_id=pk,
        )

        if not favorite.exists():
            return Response(
                {
                    'errors':
                    'Рецепт отсутствует в избранном.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            IsAuthenticated
        ],
    )
    def shopping_cart(
        self,
        request,
        pk=None,
    ):
        return self.add_relation(
            request,
            pk,
            ShoppingCart,
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(
        self,
        request,
        pk=None,
    ):
        shopping_cart = (
            ShoppingCart.objects.filter(
                user=request.user,
                recipe_id=pk,
            )
        )

        if not shopping_cart.exists():
            return Response(
                {
                    'errors':
                    'Рецепт отсутствует в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        shopping_cart.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
