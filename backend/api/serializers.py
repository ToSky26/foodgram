from collections import Counter

from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import (MINIMUM_RECIPE_COOKING_TIME,
                               MINIMUM_INGREDIENT_AMOUNT)

from recipes.models import (Subscription, Tag, Recipe,
                            RecipeIngredient, Ingredient)
from recipes.models import User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            *DjoserUserSerializer.Meta.fields,
            'avatar',
            'is_subscribed',
        )
        read_only_fields = fields

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user,
                author=user,
            ).exists()
        )


class UserExtendedSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, user):
        request = self.context.get('request')
        recipes = user.recipes.all()
        if request is not None:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                recipes = recipes[: int(recipes_limit)]

        return RecipeShortReadSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = fields


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')
    amount = serializers.IntegerField(min_value=MINIMUM_INGREDIENT_AMOUNT)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MINIMUM_RECIPE_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time']

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Поле не может быть пустым'
            )
        return image

    def validate_unique_items(self, items, field_name, key=None):
        if key:
            values = [item[key].id for item in items]
        else:
            values = [item.id if hasattr(item, 'id')
                      else item for item in items]

        duplicates = [
            item for item, count in Counter(values).items()
            if count > 1
        ]

        if duplicates:
            raise serializers.ValidationError({
                field_name: f'Повторения: {duplicates}'
            })

    def validate(self, data):
        required_fields = ['tags', 'ingredients', 'name',
                           'text', 'cooking_time', ]

        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError({
                    field: 'Обязательное поле'
                })
            if not data[field]:
                raise serializers.ValidationError({
                    field: 'Поле не может быть пустым'
                })

        self.validate_unique_items(
            data['ingredients'],
            'ingredients',
            key='ingredient'
        )

        self.validate_unique_items(
            data['tags'],
            'tags'
        )
        return data

    def set_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['ingredient'].id,
                amount=item['amount']
            )
            for item in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        instance.recipe_ingredients.all().delete()
        self.set_ingredients(
            instance,
            validated_data.pop('ingredients')
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time']
        read_only_fields = fields


class RecipeShortReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = fields
