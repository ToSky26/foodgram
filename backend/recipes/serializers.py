from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


from .models import Tag, Recipe, RecipeIngredient, Ingredient
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):

    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time']

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError({
                'image': 'Поле не может быть пустым'
            })
        return value

    def validate_unique_items(self, items, field_name, key=None):
        seen = set()
        for item in items:
            value = item[key] if key else item

            if value in seen:
                raise serializers.ValidationError({
                    field_name: 'Повторений быть не должно'
                })
            seen.add(value)

    def validate(self, data):
        required_fields = [
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        ]
        for field in required_fields:
            value = data.get(field)
            if field not in data:
                raise serializers.ValidationError({
                    field: 'Обязательное поле'
                })
            if not value:
                raise serializers.ValidationError({
                    field: 'Поле не может быть пустым'
                })

        self.validate_unique_items(data['ingredients'], 'ingredients', 'id')
        self.validate_unique_items(data['tags'], 'tags')
        return data

    def set_ingredients(self, recipe, ingredients):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount'],
            )
            for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        instance.tags.set(tags)
        self.set_ingredients(instance, ingredients)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.set_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image.url if obj.image else ''

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time']


class RecipeShortSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image.url if obj.image else ''

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
