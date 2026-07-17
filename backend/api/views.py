from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)

from api.filters import (
    IngredientFilter,
    RecipeFilter,
)

from api.permissions import (
    IsAuthorOrReadOnly,
)

from api.serializers.recipe_serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)

from api.utils import generate_shopping_list


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = (
        Recipe.objects
        .select_related('author')
        .prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )
    )

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )

    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in (
            'create',
            'update',
            'partial_update',
        ):
            return RecipeWriteSerializer

        return RecipeReadSerializer

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(
        self,
        request
    ):
        content = generate_shopping_list(
            request.user
        )

        response = HttpResponse(
            content,
            content_type='text/plain'
        )

        response[
            'Content-Disposition'
        ] = (
            'attachment; '
            'filename=shopping_list.txt'
        )

        return response

    def add_relation(
        self,
        request,
        pk,
        model
    ):
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        if model.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {
                    'errors':
                    'Рецепт уже добавлен.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.create(
            user=request.user,
            recipe=recipe
        )

        return Response(
            RecipeShortSerializer(
                recipe
            ).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(
        self,
        request,
        pk=None
    ):
        return self.add_relation(
            request,
            pk,
            Favorite
        )

    @favorite.mapping.delete
    def delete_favorite(
        self,
        request,
        pk=None
    ):
        favorite = Favorite.objects.filter(
            user=request.user,
            recipe_id=pk
        )

        if not favorite.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(
        self,
        request,
        pk=None
    ):
        return self.add_relation(
            request,
            pk,
            ShoppingCart
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(
        self,
        request,
        pk=None
    ):
        shopping_cart = (
            ShoppingCart.objects.filter(
                user=request.user,
                recipe_id=pk
            )
        )

        if not shopping_cart.exists():
            return Response(
                {
                    'errors':
                    'Рецепт отсутствует в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
