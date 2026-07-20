from django.db.models import (BooleanField, Exists, OuterRef, Sum, Value,)
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, UserExtendedSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             RecipeShortReadSerializer, TagSerializer,
                             IngredientSerializer,)
from recipes.models import (Subscription, Recipe, Tag, Ingredient,
                            RecipeIngredient,)
from recipes.services.shopping_cart import create_shopping_cart_text


class UserViewSet(DjoserUserViewSet):

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        if request.user.avatar:
            request.user.avatar.delete(save=False)

        serializer.save()

        return Response(serializer.data)

    @avatar.mapping.delete
    def avatar_delete(self, request):
        if request.user.avatar:
            request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save(update_fields=('avatar',))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_relation(self, author_id, adding):
        user = self.request.user
        if not adding:
            get_object_or_404(
                Subscription,
                user=user,
                author_id=author_id,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = self.get_object()
        if user == author:
            raise ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            author=author,
        )

        if not created:
            raise ValidationError(
                f'Вы уже подписаны на пользователя "{author.username}".'
            )

        return Response(
            UserExtendedSerializer(
                author,
                context={'request': self.request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        return self.handle_relation(pk, True)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        return self.handle_relation(pk, False)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        return self.get_paginated_response(UserExtendedSerializer(
            self.paginate_queryset(self.request.user.subscriptions.all()),
            many=True, context={'request': request}).data)


class RecipeViewSet(ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
    ]

    def get_queryset(self):
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'recipe_ingredients__ingredient',
            'tags'
        )

        user = self.request.user

        if user.is_anonymous:
            return queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField()),
            )

        return queryset.annotate(
            is_favorited=Exists(
                user.favorite.filter(
                    recipe_id=OuterRef('id'))
            ),
            is_in_shopping_cart=Exists(
                user.shopping_cart.filter(
                    recipe_id=OuterRef('id'))
            ),
        )

    def get_serializer_class(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS',):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def handle_relation(self, relation_name, adding=False):
        user = self.request.user
        through = getattr(user, relation_name).model

        relation = through.objects.filter(
            user=user, recipe_id=self.kwargs['pk']
        )

        if not adding:
            deleted, _ = relation.delete()
            if not deleted:
                raise serializers.ValidationError('Рецепт не найден в списке')
            return Response(status=status.HTTP_204_NO_CONTENT)

        if relation.exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {relation_name}')

        through.objects.create(user=user, recipe_id=self.kwargs['pk'])
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        serializer = RecipeShortReadSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='favorite')
    def favorite(self, request, pk=None):
        return self.handle_relation('favorite', pk, True)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        return self.handle_relation('favorite', pk)

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        return self.handle_relation('shopping_cart', pk, True)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        return self.handle_relation('shopping_cart', pk)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')

        recipes = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).select_related(
            'author'
        ).prefetch_related('tags')

        shopping_cart_text = create_shopping_cart_text(ingredients, recipes)

        return FileResponse(shopping_cart_text, as_attachment=True,
                            filename='shopping_cart.txt')

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        short_link = get_object_or_404(
            Recipe.objects.values_list('short_link', flat=True), pk=pk)

        return Response({'short-link': request.build_absolute_uri(
                        reverse('short-link', kwargs={'short_link': short_link}
                                ))})


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
