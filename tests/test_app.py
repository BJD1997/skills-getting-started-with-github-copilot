import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


# =====================
# GET /activities tests
# =====================

def test_get_activities_returns_all_activities(client):
    """Test that all activities are returned."""
    # Arrange
    # (no setup needed - activities are predefined)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities


def test_get_activities_includes_participant_info(client):
    """Test that activity data includes required fields."""
    # Arrange
    # (no setup needed)

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    first_activity = activities["Chess Club"]
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


# =====================
# POST /signup tests
# =====================

def test_signup_success_adds_participant(client):
    """Test that a new participant is successfully added."""
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]


def test_signup_duplicate_rejected(client):
    """Test that duplicate signups are rejected."""
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    # Act - First signup
    response1 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Act - Attempt duplicate signup
    response2 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_invalid_activity_returns_404(client):
    """Test that signup for non-existent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# =====================
# DELETE /unregister tests
# =====================

def test_unregister_success_removes_participant(client):
    """Test that a participant is successfully unregistered."""
    # Arrange
    activity_name = "Gym Class"
    email = "unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    # Verify participant removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up_returns_400(client):
    """Test that unregistering someone not signed up returns 400."""
    # Arrange
    activity_name = "Art Studio"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_invalid_activity_returns_404(client):
    """Test that unregister from non-existent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# =====================
# Integration tests
# =====================

def test_signup_then_unregister_flow(client):
    """Test complete flow: signup, verify, then unregister."""
    # Arrange
    activity_name = "Drama Club"
    email = "flow@mergington.edu"

    # Act - Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert - Signup successful
    assert signup_response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

    # Act - Unregister
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert - Unregister successful
    assert unregister_response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
