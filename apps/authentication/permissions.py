from rest_framework.permissions import BasePermission


class IsSystemAdmin(BasePermission):
    message = "Only system admins can perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.is_system_user and user.role == user.Role.ADMIN


class IsTenantAdmin(BasePermission):
    message = "Only tenant admins can perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_tenant_user
            and user.role == user.Role.ADMIN
            and user.tenant_id is not None
        )
