from django.db.models import Sum, Exists, OuterRef, Value, BooleanField
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter, IngredientFilter
from .models import Recipe, Tag, Ingredient, RecipeIngredient
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeReadSerializer,
    RecipeCreateSerializer,
    RecipeShortSerializer,
    TagSerializer,
    IngredientSerializer
)


class RecipeViewSet(ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options'
    ]

    def get_queryset(self):
        qs = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'recipe_ingredients__ingredient',
            'tags'
        )

        user = self.request.user

        if user.is_anonymous:
            return qs.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return qs.annotate(
            is_favorited=Exists(
                user.favorites.filter(id=OuterRef('id'))
            ),
            is_in_shopping_cart=Exists(
                user.shopping_cart.filter(id=OuterRef('id'))
            )
        )

    def get_serializer_class(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def handle_relation(self, field, adding=False):
        user = self.request.user
        recipe = self.get_object()
        through = getattr(user, field).through

        if adding:
            _, created = through.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'message': 'Уже добавлено'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = through.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {'message': 'Не найдено'}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='favorite')
    def favorite(self, request, pk):
        return self.handle_relation('favorites', True)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        return self.handle_relation('favorites')

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        return self.handle_relation('shopping_cart', True)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        return self.handle_relation('shopping_cart')

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_in_cart = RecipeIngredient.objects.filter(
            recipe__in_carts=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )

        for item in ingredients_in_cart:
            response.write(
                f"{item['ingredient__name']} — "
                f"{item['total_amount']} "
                f"{item['ingredient__measurement_unit']}\n"
            )

        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk):
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f'/s/{recipe.short_link}/')
        return Response({'short-link': short_url})


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None
    queryset = Tag.objects.all()
    http_method_names = ['get', ]


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()
    http_method_names = ['get', ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientFilter
