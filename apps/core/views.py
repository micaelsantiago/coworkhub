from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.tenants.services import validate_subdomain_availability


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


def landing_page(request):
    """Renderiza a landing page institucional do Coworkhub."""
    return render(request, "pages/landing.html")


@require_http_methods(["GET", "POST"])
def check_subdomain(request):
    """
    Endpoint de validação assíncrona de subdomínio para HTMX.
    Retorna o fragmento HTML com o status de disponibilidade do slug.
    """
    subdomain_input = request.POST.get("subdomain") or request.GET.get("subdomain", "")
    result = validate_subdomain_availability(subdomain_input)

    return render(
        request,
        "components/subdomain_check_result.html",
        {"result": result},
    )
