from datetime import datetime

INGREDIENT_TEMPLATE = ('{index}. {name} — {amount} {measurement_unit}')

RECIPE_TEMPLATE = ('{index} {name} {author} {tags}')


def create_shopping_cart_text(ingredients, recipes):
    return '\n'.join([
        'Список покупок',
        f'Дата составления: {datetime.now():%d.%m.%Y}',
        '',
        'Продукты:',
        *[
            INGREDIENT_TEMPLATE.format(
                index=index,
                name=item['ingredient__name'].capitalize(),
                amount=item['amount'],
                measurement_unit=item['ingredient__measurement_unit'],
            )
            for index, item in enumerate(ingredients, start=1)
        ],
        '',
        'Рецепты:',
        *[
            RECIPE_TEMPLATE.format(
                index=index,
                name=recipe.name,
                author=recipe.author.username,
                tags=', '.join(
                    tag.name for tag in recipe.tags.all()
                ),
            )
            for index, recipe in enumerate(recipes, start=1)
        ],
    ])
