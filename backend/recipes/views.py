from django.shortcuts import redirect

from .models import Recipe


def short_link_redirect(request, recipe_id):
    recipe_pk = (
        Recipe.objects
        .filter(short_link=recipe_id)
        .values_list('id', flat=True)
        .first()
    )

    if not recipe_pk:
        return redirect('/404')

    return redirect(f'/recipes/{recipe_id}/')
