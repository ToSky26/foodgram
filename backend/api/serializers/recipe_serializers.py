from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from users.models import User

from .user_serializers import UserSerializer


class TagSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(
    serializers.ModelSerializer
):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )

    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )

    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeShortSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeReadSerializer(
    serializers.ModelSerializer
):
    tags = TagSerializer(
        many=True,
        read_only=True
    )

    author = UserSerializer(
        read_only=True
    )

    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )

    is_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe

        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(
        self,
        obj
    ):
        request = self.context.get(
            'request'
        )

        if (
            request is None
            or request.user.is_anonymous
        ):
            return False

        return obj.favorited_by.filter(
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(
        self,
        obj
    ):
        request = self.context.get(
            'request'
        )

        if (
            request is None
            or request.user.is_anonymous
        ):
            return False

        return obj.in_carts.filter(
            user=request.user
        ).exists()


class RecipeIngredientCreateSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    amount = serializers.IntegerField()


class RecipeWriteSerializer(
    serializers.ModelSerializer
):
    image = Base64ImageField()

    ingredients = (
        RecipeIngredientCreateSerializer(
            many=True
        )
    )

    tags = (
        serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all(),
            many=True
        )
    )

    class Meta:
        model = Recipe

        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(
        self,
        attrs
    ):
        ingredients = attrs.get(
            'ingredients'
        )

        tags = attrs.get(
            'tags'
        )

        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients':
                    'Добавьте ингредиенты.'
                }
            )

        if not tags:
            raise serializers.ValidationError(
                {
                    'tags':
                    'Добавьте теги.'
                }
            )

        ingredient_ids = [
            item['id']
            for item in ingredients
        ]

        if len(
            ingredient_ids
        ) != len(
            set(ingredient_ids)
        ):
            raise serializers.ValidationError(
                {
                    'ingredients':
                    'Ингредиенты не должны повторяться.'
                }
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {
                    'tags':
                    'Теги не должны повторяться.'
                }
            )

        return attrs

    def create_ingredients(
        self,
        recipe,
        ingredients
    ):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=item['id'],
                    amount=item['amount']
                )
                for item in ingredients
            ]
        )

    def create(
        self,
        validated_data
    ):
        ingredients = (
            validated_data.pop(
                'ingredients'
            )
        )

        tags = (
            validated_data.pop(
                'tags'
            )
        )

        recipe = Recipe.objects.create(
            author=self.context[
                'request'
            ].user,
            **validated_data
        )

        recipe.tags.set(tags)

        self.create_ingredients(
            recipe,
            ingredients
        )

        return recipe

    def update(
        self,
        instance,
        validated_data
    ):
        ingredients = (
            validated_data.pop(
                'ingredients'
            )
        )

        tags = (
            validated_data.pop(
                'tags'
            )
        )

        instance.tags.set(tags)

        instance.recipe_ingredients.all().delete()

        self.create_ingredients(
            instance,
            ingredients
        )

        for attr, value in (
            validated_data.items()
        ):
            setattr(
                instance,
                attr,
                value
            )

        instance.save()

        return instance

    def to_representation(
        self,
        instance
    ):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()

    recipes_count = (
        serializers.IntegerField(
            source='recipes.count',
            read_only=True
        )
    )

    class Meta():
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(
        self,
        obj
    ):
        request = self.context[
            'request'
        ]

        limit = request.GET.get(
            'recipes_limit'
        )

        recipes = obj.recipes.all()

        if limit:
            recipes = recipes[
                :int(limit)
            ]

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context
        ).data
