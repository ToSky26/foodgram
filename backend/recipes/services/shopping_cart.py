from datetime import datetime


def create_shopping_cart_text(ingredients, recipes):
    return '\n'.join([
        'Список покупок',
        f'Дата составления: {datetime.now():%d.%m.%Y}',
        '',
        'Продукты:',
        *[
            (
                f'{index}. '
                f'{item["ingredient__name"].capitalize()} — '
                f'{item["amount"]} '
                f'{item["ingredient__measurement_unit"]}'
            )
            for index, item in enumerate(ingredients, start=1)
        ],
        '',
        'Рецепты:',
        *[
            (
                f'{index}. {recipe.name} '
                f'(@{recipe.author.username})'
            )
            for index, recipe in enumerate(recipes, start=1)
        ],
    ])
