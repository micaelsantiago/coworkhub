from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def healthz(request):
    return JsonResponse({"status": "ok"})


def readyz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        cache.set("readiness", "ok", timeout=5)
        if cache.get("readiness") != "ok":
            raise ConnectionError("Redis indisponível")
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
