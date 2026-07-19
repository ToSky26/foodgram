from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import UserExtendedSerializer
from .serializers import AvatarSerializer


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели пользователя."""

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def avatar_delete(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_relation(self, adding=False):
        user = self.request.user
        author = self.get_object()
        through = user.subscriptions.through
        if adding:
            if user == author:
                return Response(
                    {'message': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            _, created = through.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                return Response(
                    {'message': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserExtendedSerializer(
                instance=author,
                context={'request': self.request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = through.objects.filter(
            user=user,
            author=author
        ).delete()
        if not deleted:
            return Response(
                {'message': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        return self.handle_relation(True)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk):
        return self.handle_relation()

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = self.request.user.subscriptions.all()
        page = self.paginate_queryset(subscriptions)
        serializer = UserExtendedSerializer(
            page, many=True, 
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
