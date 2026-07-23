from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from .models import Recipe
from .utils import decode_recipe_id


def short_link_redirect(request, short_code):
    recipe_id = decode_recipe_id(short_code)

    if recipe_id is None:
        raise Http404('Некорректная короткая ссылка.')

    recipe = Recipe.objects.filter(
        id=recipe_id
    ).first()

    if recipe is None:
        raise Http404(
            f'Рецепт с id={recipe_id} не найден.'
        )

    return redirect(
        reverse(
            'recipes-detail',
            args=[recipe.id]
        )
    )
