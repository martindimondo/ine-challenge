from oauth2_provider.models import Application
import pytest

from ..models import User
from .dependencies import (
    as_non_staff_token,
    as_nonstaff,
    as_staff,
    as_staff_token,
    create_app,
    create_user_payload,
    TEST_STAFF_USERNAME,
    TEST_NONSTAFF_USERNAME,
    TEST_NONSTAFF_PASSWORD,
    TEST_STAFF_PASSWORD,
)


ENDPOINT_USER = "/api/v1/users/"


@pytest.mark.django_db
def test_create_user_unauthenticated(client, create_app):
    payload = create_user_payload("foo", "p121212Ab", "p121212Ab", [])

    response = client.post(
        ENDPOINT_USER,
        data=payload,
    )

    assert (
        response.status_code == 401
    ), "Users can't be added without authentication"


@pytest.mark.django_db
def test_create_user_as_staff(as_staff_token, client):
    payload = create_user_payload("foo3", "p121212Ab", "p121212Ab", ["sales"])
    response = client.post(
        ENDPOINT_USER,
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )
    assert response.status_code == 201

    data = response.json()
    assert data.get("password") is not None, "Password must not be null"
    assert len(data["groups"]) == 1, "Groups quantity must be 1"
    assert data["id"] is not None, "Id can't be null"
    assert data["username"] == "foo3", "Username doesn't match"


@pytest.mark.django_db
def test_create_user_bad_pass_as_staff(as_staff_token, client):
    payload = create_user_payload(
        "foo3", "p121212Ab", "p1212344412Ab", ["sales"]
    )
    response = client.post(
        ENDPOINT_USER,
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )
    assert response.status_code == 400
    json = response.json()
    assert len(json["repeat_password"]) > 0, "Repeat password is invalid"


@pytest.mark.django_db
def test_create_user_as_non_staff(as_non_staff_token, client):
    payload = create_user_payload("foo4", "p121212Ab", "p121212Ab", ["sales"])
    response = client.post(
        ENDPOINT_USER,
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )
    assert response.status_code == 403, "Staff user required"


@pytest.mark.django_db
def test_read_user_as_staff(as_staff_token, client):
    user = User.objects.get(username=TEST_STAFF_USERNAME)
    response = client.get(
        f"{ENDPOINT_USER}{user.id}/",
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )

    data = response.json()

    assert data.get("password") is not None, "Password must not be none"
    assert data["id"] == str(user.id), "User id doesn't match"
    assert data["username"] == user.username, "Username doesn't match"


@pytest.mark.django_db
def test_read_user_as_non_staff(as_non_staff_token, client):
    user = User.objects.get(username=TEST_STAFF_USERNAME)
    response = client.get(
        f"{ENDPOINT_USER}{user.id}/",
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )

    data = response.json()

    assert data.get("password") is None, "Password must be none"
    assert data.get("updated") is None, "User updated must not be none"
    assert data["id"] == str(user.id), "User id doesn't match"
    assert data["username"] == user.username, "Username doesn't match"

    user = User.objects.get(username=TEST_NONSTAFF_USERNAME)
    response = client.get(
        f"{ENDPOINT_USER}{user.id}/",
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )
    data = response.json()
    assert (
        data.get("password") is not None
    ), "Self user password must not be none"
    assert (
        data.get("updated") is not None
    ), "Self user updated must not be none"
    assert data["id"] == str(user.id), "User id doesn't match"
    assert data["username"] == user.username, "Username doesn't match"


@pytest.mark.django_db
def test_read_user_as_unauthenciated(as_nonstaff, client):
    user = User.objects.get(username=TEST_NONSTAFF_USERNAME)
    response = client.get(
        f"{ENDPOINT_USER}{user.id}/", content_type="application/json"
    )

    assert response.status_code == 401, "Must be authenticated"


@pytest.mark.django_db
def test_full_update_user_as_staff(as_staff_token, client):
    user = User.objects.get(username=TEST_STAFF_USERNAME)
    payload = {
        "username": TEST_STAFF_USERNAME,
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@ine.test",
        "password": "SuperSecureNewPasswd",
        "old_password": "SuperSecurePasswd",
        "groups": [
            "sales",
            "support",
        ],
    }

    response = client.put(
        f"{ENDPOINT_USER}{user.id}/",
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )

    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == "John"
    assert data["id"] == str(user.id)
    assert len(data["groups"]) == 2


@pytest.mark.django_db
def test_full_update_user_invalid_as_non_staff(as_non_staff_token, client):
    user = User.objects.get(username=TEST_STAFF_USERNAME)
    payload = {
        "username": TEST_STAFF_USERNAME,
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@ine.test",
        "password": "SuperSecureNewPasswd",
        "old_password": TEST_STAFF_PASSWORD,
        "groups": [
            "sales",
            "support",
        ],
    }

    response = client.put(
        f"{ENDPOINT_USER}{user.id}/",
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_full_update_user_valid_as_non_staff(as_non_staff_token, client):
    user = User.objects.get(username=TEST_NONSTAFF_USERNAME)
    payload = {
        "username": TEST_NONSTAFF_USERNAME,
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@ine.test",
        "password": "SuperSecureNewPasswd",
        "old_password": TEST_NONSTAFF_PASSWORD,
        "groups": [
            "sales",
            "support",
        ],
    }

    response = client.put(
        f"{ENDPOINT_USER}{user.id}/",
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_partial_update_user_as_staff(as_staff_token, client):
    user = User.objects.get(username=TEST_STAFF_USERNAME)
    payload = {
        "first_name": "Johncito",
        "last_name": "Doe",
    }

    response = client.patch(
        f"{ENDPOINT_USER}{user.id}/",
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] is not None
    assert data["first_name"] == "Johncito"


@pytest.mark.django_db
def test_partial_update_user_as_non_staff(as_non_staff_token, client):
    user = User.objects.get(username=TEST_NONSTAFF_USERNAME)
    payload = {
        "first_name": "Johncito",
        "last_name": "Doe",
    }

    response = client.patch(
        f"{ENDPOINT_USER}{user.id}/",
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )
    assert response.status_code == 400, "Old password not provided"

    payload = {
        "first_name": "Pepe",
        "last_name": "Pompin",
        "old_password": TEST_NONSTAFF_PASSWORD,
    }

    response = client.patch(
        f"{ENDPOINT_USER}{user.id}/",
        data=payload,
        content_type="application/json",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] is not None
    assert data["first_name"] == "Pepe"


@pytest.mark.django_db
def test_delete_user_as_non_staff(as_non_staff_token, client):
    user = User.objects.get(username=TEST_NONSTAFF_USERNAME)

    response = client.delete(
        f"{ENDPOINT_USER}{user.id}/",
        AUTHORIZATION=f"Bearer {as_non_staff_token}",
    )
    assert response.status_code == 403, "Non staff cant delete"


@pytest.mark.django_db
def test_delete_user_as_non_staff(as_staff_token, client):
    user_staff = User.objects.get(username=TEST_STAFF_USERNAME)
    user = User.objects.get(username=TEST_NONSTAFF_USERNAME)

    response = client.delete(
        f"{ENDPOINT_USER}{user_staff.id}/",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )
    assert response.status_code == 403, "staff cant delete by another staff"

    response = client.delete(
        f"{ENDPOINT_USER}{user.id}/",
        AUTHORIZATION=f"Bearer {as_staff_token}",
    )
    assert response.status_code == 204, "staff can delete non staff"
