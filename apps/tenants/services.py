import re
from typing import NamedTuple

from django.apps import apps
from django.utils.text import slugify

RESERVED_SUBDOMAINS: frozenset[str] = frozenset(
    {
        "admin",
        "api",
        "app",
        "billing",
        "cdn",
        "dashboard",
        "help",
        "mail",
        "media",
        "portal",
        "root",
        "static",
        "status",
        "suporte",
        "test",
        "webhook",
        "ws",
        "www",
    }
)

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MIN_SUBDOMAIN_LENGTH = 2
MAX_SUBDOMAIN_LENGTH = 63


class SubdomainValidationResult(NamedTuple):
    is_valid: bool
    slug: str
    error: str | None = None


def normalize_subdomain_slug(value: str) -> str:
    """Normaliza o nome do coworking em um slug válido para subdomínio."""
    return slugify(value or "").strip()


def validate_subdomain_availability(name_or_slug: str) -> SubdomainValidationResult:
    """
    Valida formato, tamanho e disponibilidade contra subdomínios reservados
    e registros existentes no banco de dados.
    """
    slug = normalize_subdomain_slug(name_or_slug)

    if not slug:
        return SubdomainValidationResult(
            is_valid=False,
            slug="",
            error="Informe o nome ou subdomínio desejado para o seu espaço.",
        )

    if len(slug) < MIN_SUBDOMAIN_LENGTH:
        return SubdomainValidationResult(
            is_valid=False,
            slug=slug,
            error=f"O subdomínio deve ter pelo menos {MIN_SUBDOMAIN_LENGTH} caracteres.",
        )

    if len(slug) > MAX_SUBDOMAIN_LENGTH:
        return SubdomainValidationResult(
            is_valid=False,
            slug=slug,
            error=f"O subdomínio deve ter no máximo {MAX_SUBDOMAIN_LENGTH} caracteres.",
        )

    if not SLUG_PATTERN.match(slug):
        return SubdomainValidationResult(
            is_valid=False,
            slug=slug,
            error="O subdomínio só pode conter letras minúsculas, números e hifens.",
        )

    if slug in RESERVED_SUBDOMAINS:
        return SubdomainValidationResult(
            is_valid=False,
            slug=slug,
            error=f"O endereço '{slug}' é reservado pelo sistema. Por favor, escolha outro nome.",
        )

    # Checa unicidade caso o model Domain já exista no banco
    if apps.is_installed("apps.tenants"):
        try:
            Domain = apps.get_model("tenants", "Domain")
            if Domain.objects.filter(name=slug).exists():
                return SubdomainValidationResult(
                    is_valid=False,
                    slug=slug,
                    error=f"O endereço '{slug}' já está em uso por outro coworking.",
                )
        except LookupError:
            pass

    return SubdomainValidationResult(is_valid=True, slug=slug, error=None)
