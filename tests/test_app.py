"""
Tests for the Mergington High School API using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary to a known state before each test."""
    original_state = {name: {**data, "participants": list(data["participants"])} for name, data in activities.items()}
    yield
    activities.clear()
    activities.update(original_state)


client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Arrange - client is set up via TestClient

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        # Arrange - client is set up via TestClient

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_contains_literary_journal(self):
        # Arrange - default activities include Literary Journal

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "Literary Journal" in data

    def test_get_activities_have_required_fields(self):
        # Arrange - default activities

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignupForActivity:
    def test_signup_returns_200_on_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_signup_adds_student_to_participants(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_success_message(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_returns_404_for_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_signup_prevents_duplicate_registration(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up in default data

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    def test_unregister_returns_200_on_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up in default data

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_student_from_participants(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_returns_success_message(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_returns_404_for_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_returns_400_if_not_signed_up(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
