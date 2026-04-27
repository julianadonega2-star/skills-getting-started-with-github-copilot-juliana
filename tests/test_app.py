import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for testing."""
    return TestClient(app)


def test_get_activities(client):
    """Test GET /activities returns all activities."""
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_root_redirect(client):
    """Test GET / redirects to static homepage."""
    # Arrange - No special setup needed

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    email = "newsignup@example.com"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity}" == data["message"]

    # Verify participant was added
    response2 = client.get("/activities")
    data2 = response2.json()
    assert email in data2[activity]["participants"]


def test_signup_duplicate(client):
    """Test signup fails for duplicate email."""
    # Arrange
    email = "duplicate@example.com"
    activity = "Chess Club"

    # Act - First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act - Second signup (should fail)
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client):
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@example.com"
    activity = "NonExistentActivity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_success(client):
    """Test successful removal from an activity."""
    # Arrange
    email = "todelete@example.com"
    activity = "Programming Class"

    # First, sign up
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/signup/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email} from {activity}" == data["message"]

    # Verify participant was removed
    response2 = client.get("/activities")
    data2 = response2.json()
    assert email not in data2[activity]["participants"]


def test_delete_not_signed_up(client):
    """Test delete fails for email not signed up."""
    # Arrange
    email = "notsigned@example.com"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup/{email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()


def test_delete_nonexistent_activity(client):
    """Test delete fails for non-existent activity."""
    # Arrange
    email = "test@example.com"
    activity = "NonExistentActivity"

    # Act
    response = client.delete(f"/activities/{activity}/signup/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()