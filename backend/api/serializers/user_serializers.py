from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if (
            request is None
            or request.user.is_anonymous
        ):
            return False

        return obj.subscribers.filter(
            user=request.user
        ).exists()


class FoodgramUserCreateSerializer(
    UserCreateSerializer
):
    first_name = serializers.CharField(
        required=True
    )

    last_name = serializers.CharField(
        required=True
    )

    class Meta(
        UserCreateSerializer.Meta
    ):
        model = User

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
