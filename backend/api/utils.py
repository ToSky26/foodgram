from django.db.models import Sum
from recipes.models import RecipeIngredient


def generate_shopping_list(user):
    ingredients = (
        RecipeIngredient.objects
        .filter(recipe__in_carts__user=user)
        .values(
            'ingredient__name',
            'ingredient__measurement_unit'
        )
        .annotate(total_amount=Sum('amount'))
    )

    shopping_list = []

    for item in ingredients:
        shopping_list.append(
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) "
            f"- {item['total_amount']}"
        )

    return '\n'.join(shopping_list)
