from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.subscriptions.filter(id=obj.id).exists()
        )

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar']


class UserExtendedSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        from recipes.serializers import RecipeShortSerializer
        request = self.context.get('request')
        queryset = obj.recipes.all()
        if request:
            limit = request.query_params.get('recipes_limit')
            if limit:
                queryset = queryset[:int(limit)]
            return RecipeShortSerializer(
                queryset, many=True
            ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'recipes',
            'recipes_count'
        ]


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar', ]
