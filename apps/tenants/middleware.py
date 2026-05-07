class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            tenant = user.tenant

            request.tenant = tenant

            request.subscription = tenant.active_subscription if tenant else None

            request.subscription_active = (
                tenant.is_subscription_active if tenant else False
            )

        else:
            request.tenant = None
            request.subscription = None
            request.subscription_active = False

        return self.get_response(request)
