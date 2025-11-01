from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Разрешение, при котором коммент редактирует только автор'''

    def has_object_permission(self, request, view, obj):
        # Разрешение на запись для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешение на запись только для автора
        return obj.author == request.user