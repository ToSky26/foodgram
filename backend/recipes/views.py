from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from .models import Recipe


def short_link_redirect(request, recipe_id):
    if not Recipe.objects.filter(pk=recipe_id).exists():
        raise Http404(f'Рецепт с id={recipe_id} не найден.')

    return redirect(
        reverse('recipes-detail', args=[recipe_id])
    )
