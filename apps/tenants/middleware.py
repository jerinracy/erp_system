class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            request.tenant = user.tenant
        else:
            request.tenant = None

        return self.get_response(request)
