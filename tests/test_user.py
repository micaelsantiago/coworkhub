import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_user_authenticates_with_email():
    user = User.objects.create_user(email="user@example.com", password="test-password")

    assert user.username is None
    assert user.email == "user@example.com"
    assert user.check_password("test-password")
