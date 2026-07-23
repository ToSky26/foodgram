from datetime import datetime

INGREDIENT_TEMPLATE = (
    '{index}. {name} ({measurement_unit}) — {amount}'
)

RECIPE_TEMPLATE = ('{index} {name} (@{author}) {tags}')
MONTHS = ('', 'января', 'февраля', 'марта', 'апреля',
          'мая', 'июня', 'июля', 'августа', 'сентября',
          'октября', 'ноября', 'декабря',)


def create_shopping_cart_text(ingredients, recipes):
    today = datetime.now()
    date = (
        f'{today.day:02d} '
        f'{MONTHS[today.month]} '
        f'{today.year}'
    )
    return '\n'.join([
        'Список покупок',
        f'Дата составления: {date}',

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
                    f'#{tag.name}' for tag in recipe.tags.all()
                ),
            )
            for index, recipe in enumerate(recipes, start=1)
        ],
    ])
