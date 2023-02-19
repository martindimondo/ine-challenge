import uuid
from ..subscription import subscription_service


def test_subscription():
    id = str(uuid.uuid4())
    response = subscription_service.fetch_subscription(id)

    assert response["subscription"] == "active", "Failed on subscription fetch"
