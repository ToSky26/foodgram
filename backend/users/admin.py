from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


from django.db.models import Count


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'recipe_count')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('recipe_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipes')
        )

    @admin.display(description='Создал рецептов')
    def recipe_count(self, obj):
        return obj.recipe_count


admin.site.unregister(Group)
