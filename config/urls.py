from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from apps.core.views import healthz, readyz

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
]
