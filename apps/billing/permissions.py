from rest_framework.permissions import BasePermission


class HasActiveSubscription(BasePermission):
    message = "Subscription expired"

    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser:
            return True

        tenant = getattr(user, "tenant", None)

        if not tenant:
            return False

        return tenant.is_subscription_active
