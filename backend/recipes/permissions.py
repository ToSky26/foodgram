from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Пермишн для проверки авторства рецепта."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.method in SAFE_METHODS