import pytest
from django.urls import reverse

from apps.tenants.services import (
    RESERVED_SUBDOMAINS,
    normalize_subdomain_slug,
    validate_subdomain_availability,
)


def test_landing_page_renders_successfully(client):
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    assert "Acabe com os conflitos de sala" in response.content.decode("utf-8")
    assert "Criar meu espaço" in response.content.decode("utf-8")
    assert "Plano Operação" in response.content.decode("utf-8")


def test_check_subdomain_valid(client):
    url = reverse("check_subdomain")
    response = client.post(url, {"subdomain": "estacao-coworking"})

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Disponível:" in content
    assert "estacao-coworking.coworkhub.com.br" in content
    assert 'value="estacao-coworking"' in content


def test_check_subdomain_normalizes_name(client):
    url = reverse("check_subdomain")
    response = client.post(url, {"subdomain": "Espaço Inovação & Café!"})

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Disponível:" in content
    assert "espaco-inovacao-cafe.coworkhub.com.br" in content


def test_check_subdomain_rejects_reserved(client):
    url = reverse("check_subdomain")
    response = client.post(url, {"subdomain": "admin"})

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "reservado pelo sistema" in content


def test_check_subdomain_rejects_empty(client):
    url = reverse("check_subdomain")
    response = client.post(url, {"subdomain": "   "})

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Informe o nome ou subdomínio desejado" in content


def test_check_subdomain_rejects_too_short(client):
    url = reverse("check_subdomain")
    response = client.post(url, {"subdomain": "x"})

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "pelo menos 2 caracteres" in content


@pytest.mark.parametrize("reserved", list(RESERVED_SUBDOMAINS)[:5])
def test_subdomain_service_reserved_words(reserved):
    result = validate_subdomain_availability(reserved)
    assert not result.is_valid
    assert "reservado" in (result.error or "")


def test_subdomain_service_normalization():
    assert normalize_subdomain_slug("Coworking São Paulo") == "coworking-sao-paulo"
    assert normalize_subdomain_slug(" HUB-01 ") == "hub-01"
