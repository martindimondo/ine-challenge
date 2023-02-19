from oauth2_provider.models import Application
import pytest
from ..models import User


TEST_STAFF_USERNAME = "foo"
TEST_STAFF_PASSWORD = "foO1234FFF"

TEST_NONSTAFF_USERNAME = "bar"
TEST_NONSTAFF_PASSWORD = "barO1234FFF"

TEST_CLIENT_ID = "client_id"
TEST_CLIENT_SECRET = "client_secret"


@pytest.fixture
def create_app():
    application = Application(
        name="Test Application",
        redirect_uris="http://localhost",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
    )
    application.save()

    foo_user = User()
    foo_user.first_name = "foo"
    foo_user.last_name = "foo"
    foo_user.email = "foo@ine.com"
    foo_user.is_staff = True
    foo_user.username = TEST_STAFF_USERNAME
    foo_user.set_password(TEST_STAFF_PASSWORD)
    foo_user.save()

    bar_user = User()
    bar_user.first_name = "bar"
    bar_user.last_name = "bar"
    bar_user.email = "bar@ine.com"
    bar_user.is_staff = False
    bar_user.username = TEST_NONSTAFF_USERNAME
    bar_user.set_password(TEST_NONSTAFF_PASSWORD)

    bar_user.save()

    return application


@pytest.fixture
def as_staff(create_app, client):
    response = client.post(
        "/o/token/",
        data=f"grant_type=password&username={TEST_STAFF_USERNAME}&password={TEST_STAFF_PASSWORD}&client_id={TEST_CLIENT_ID}&client_secret={TEST_CLIENT_SECRET}",
        content_type="application/x-www-form-urlencoded",
    )
    return response.json()


@pytest.fixture
def as_nonstaff(create_app, client):
    response = client.post(
        "/o/token/",
        data=f"grant_type=password&username={TEST_NONSTAFF_USERNAME}&password={TEST_NONSTAFF_PASSWORD}&client_id={TEST_CLIENT_ID}&client_secret={TEST_CLIENT_SECRET}",
        content_type="application/x-www-form-urlencoded",
    )
    return response.json()


@pytest.fixture
def as_staff_token(as_staff):
    return as_staff["access_token"]


@pytest.fixture
def as_non_staff_token(as_nonstaff):
    return as_nonstaff["access_token"]


def create_user_payload(username, password, repassword, groups):
    return {
        "username": username,
        "first_name": username,
        "last_name": username,
        "email": f"{username}@ine.com",
        "password": password,
        "repeat_password": repassword,
        "groups": groups,
    }
