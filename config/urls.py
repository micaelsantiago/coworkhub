from django.contrib import admin
from django.urls import path

from apps.core.views import check_subdomain, healthz, landing_page, readyz

urlpatterns = [
    path("", landing_page, name="home"),
    path("check-subdomain/", check_subdomain, name="check_subdomain"),
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
]
