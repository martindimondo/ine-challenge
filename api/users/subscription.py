"""
    Subscription module
"""
import json
import re
import responses
import requests


class SubscriptionException(Exception):
    """
    Exception to represent communication errors
    """


def _mock_callback(request):
    """
    Response mock function
    """
    uid = request.url.split("/")[-1]
    resp_body = {"id": uid, "subscription": "active"}

    headers = {"Content-type": "application/json"}

    return (200, headers, json.dumps(resp_body))


# pylint: disable=R0903
class SubscriptionClient:
    """
    API Subscription client class
    """

    BASE_API_URL = "https://subscriptions.fake.service.test/api/v1/"

    def get(self, endpoint, params=None):
        """Get API function"""
        return requests.get(
            f"{self.BASE_API_URL}{endpoint}", params, timeout=60
        )


# pylint: disable=R0903
class SubscriptionClientMock(SubscriptionClient):
    """
    Class to mock subscription client
    """

    @responses.activate
    def get(self, endpoint, params=None):
        """GET API mock function"""
        responses.add_callback(
            responses.GET,
            re.compile(
                "https://subscriptions.fake.service.test/api/v1/users/*"
            ),
            callback=_mock_callback,
            content_type="application/json",
        )
        return super().get(endpoint, params)


class SubscriptionService:
    """
    Subscription service class
    """

    def __init__(self, client=SubscriptionClient()):
        self._client = client

    def fetch_subscription(self, uuid):
        """Retrieve subscription by uuid"""
        response = self._client.get(f"users/{uuid}")
        if not response.ok:
            raise SubscriptionException(response.text)
        return response.json()


subscription_service = SubscriptionService(SubscriptionClientMock())
