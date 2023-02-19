"""
    Permissions utils module
"""
from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    """
    Permission to allow only staff
    """

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsAdmin(permissions.BasePermission):
    """
    Permission to allow only admin
    """

    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class StaffDeleteNoStaff(permissions.BasePermission):
    """
    Permission to allow delete non staff users by staff
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            and request.method == "DELETE"
            and not obj.is_staff
        )


# pylint: disable=R0903
class PermissionsIsolatedMixin:
    """
    Mixin to allow define isolated permissions per method
    """

    def get_permissions(self):
        """Return permissions when it's available"""
        if self.action:
            action_method = getattr(self, self.action)
            if hasattr(action_method, "permission_classes"):
                return [perm() for perm in action_method.permission_classes]
        return super().get_permissions()
