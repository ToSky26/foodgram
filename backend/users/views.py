from api.serializers.recipe_serializers import UserWithRecipesSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import AvatarSerializer


class FoodgramUserViewSet(UserViewSet):
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)

        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(
            user=request.user,
            author=author
        )

        serializer = UserWithRecipesSerializer(
            author,
            context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        subscription = Subscription.objects.filter(
            user=request.user,
            author_id=id
        )

        if not subscription.exists():
            return Response(
                {'errors': 'Подписка отсутствует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            subscribers__user=request.user
        ).prefetch_related(
            'recipes'
        )

        serializer = UserWithRecipesSerializer(
            authors,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        serializer.save()

        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        request.user.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
