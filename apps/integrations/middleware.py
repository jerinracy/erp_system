from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import APIKey, APIKeyUsage, IPRequestLog


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Only apply to public API
        if request.path.startswith("/api/sales/public/"):

            #  STEP 1: IP RATE LIMIT (NEW - GLOBAL PROTECTION)
            ip = request.META.get("REMOTE_ADDR")  # NEW

            one_minute_ago = timezone.now() - timedelta(minutes=1)

            ip_count = IPRequestLog.objects.filter(
                ip_address=ip,
                timestamp__gte=one_minute_ago
            ).count()

            if ip_count >= 100:  # NEW LIMIT (adjustable)
                return JsonResponse({"error": "Too many requests"}, status=429)

            # log IP request
            IPRequestLog.objects.create(ip_address=ip)  # NEW

            # STEP 2: API KEY VALIDATION
            api_key = request.headers.get("X-API-KEY")

            if not api_key:
                return JsonResponse({"error": "Unauthorized"}, status=401)  # changed message

            try:
                key_obj = APIKey.objects.select_related("tenant").get(
                    key=api_key,
                    is_active=True,
                )
            except APIKey.DoesNotExist:
                return JsonResponse({"error": "Unauthorized"}, status=401)  # hide reason

            # STEP 3: API KEY RATE LIMIT (EXISTING IMPROVED)
            request_count = APIKeyUsage.objects.filter(
                api_key=key_obj,
                timestamp__gte=one_minute_ago
            ).count()

            if request_count >= 100:
                return JsonResponse({"error": "Rate limit exceeded"}, status=429)

            # log usage
            APIKeyUsage.objects.create(api_key=key_obj)

            # STEP 4: ATTACH CONTEXT (IMPORTANT)
            request.tenant = key_obj.tenant
            request.api_key = key_obj

        return self.get_response(request)
