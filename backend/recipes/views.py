from django.shortcuts import redirect

from .models import Recipe


def short_link_redirect(request, short_link):
    ''''Представление для редиректа через короткую ссылку на нормальную.'''
    try:
        recipe = Recipe.objects.get(short_link=short_link)
    except Recipe.DoesNotExist:
        return redirect('/404')
    return redirect(f'/recipes/{recipe.id}/')
