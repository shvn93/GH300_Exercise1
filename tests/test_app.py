"""
Tests for the FastAPI extracurricular activities application.
Uses the AAA (Arrange-Act-Assert) testing pattern for clarity.
"""

import pytest
from fastapi.testclient import TestClient


# ============================================================================
# ROOT ENDPOINT TESTS
# ============================================================================

class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Have a test client ready.
        Act: Make GET request to root endpoint.
        Assert: Verify redirect to /static/index.html with 307 status (temporary redirect).
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


# ============================================================================
# GET ACTIVITIES ENDPOINT TESTS
# ============================================================================

class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Test client is ready with seeded activities.
        Act: Make GET request to /activities.
        Assert: Verify response contains all activities with correct structure.
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data

    def test_get_activities_has_required_fields(self, client):
        """
        Arrange: Test client is ready.
        Act: Fetch activities.
        Assert: Verify each activity has description, schedule, max_participants, participants.
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_participants_list_format(self, client):
        """
        Arrange: Test client ready. Chess Club has initial participants.
        Act: Fetch activities.
        Assert: Verify participants are emails in a list.
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        chess_club = activities_data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


# ============================================================================
# POST SIGNUP ENDPOINT TESTS
# ============================================================================

class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Test client ready. Prepare valid email and activity.
        Act: POST signup request for new participant.
        Assert: Verify 200 response and participant added to activity.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_participant_returns_400(self, client):
        """
        Arrange: Chess Club already has michael@mergington.edu.
        Act: Try to sign up same email for same activity.
        Assert: Verify 400 error and "already signed up" message.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare request for activity that doesn't exist.
        Act: POST signup to nonexistent activity.
        Assert: Verify 404 error.
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_with_special_characters_in_email(self, client):
        """
        Arrange: Prepare email with special characters (but valid email format).
        Act: Signup with special character email.
        Assert: Verify success and participant added.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "student+tag@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_multiple_different_emails_same_activity(self, client):
        """
        Arrange: Prepare two different emails.
        Act: Sign up both to the same activity.
        Assert: Verify both were added successfully.
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email1 in activities_data[activity_name]["participants"]
        assert email2 in activities_data[activity_name]["participants"]


# ============================================================================
# DELETE PARTICIPANT ENDPOINT TESTS
# ============================================================================

class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_success(self, client):
        """
        Arrange: Chess Club has michael@mergington.edu.
        Act: DELETE request to remove that participant.
        Assert: Verify 200 response and participant removed from activity.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        
        # Verify participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Prepare request to remove participant not in activity.
        Act: DELETE request for nonexistent participant.
        Assert: Verify 404 error.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_participant_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare request for activity that doesn't exist.
        Act: DELETE request from nonexistent activity.
        Assert: Verify 404 error.
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_multiple_participants_sequentially(self, client):
        """
        Arrange: Chess Club has two participants.
        Act: Remove both participants one by one.
        Assert: Verify both removed successfully and list updated.
        """
        # Arrange
        activity_name = "Chess Club"
        email1 = "michael@mergington.edu"
        email2 = "daniel@mergington.edu"
        
        # Act - Remove first
        response1 = client.delete(
            f"/activities/{activity_name}/participants/{email1}"
        )
        
        # Act - Remove second
        response2 = client.delete(
            f"/activities/{activity_name}/participants/{email2}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data[activity_name]["participants"]) == 0

    def test_remove_participant_then_can_signup_again(self, client):
        """
        Arrange: Gym Class has john@mergington.edu.
        Act: Remove john, then signup john again.
        Assert: Verify john removed and can be added again.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Act - Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert remove_response.status_code == 200
        assert signup_response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests across multiple endpoints."""

    def test_full_signup_and_removal_workflow(self, client):
        """
        Arrange: Have a test client ready.
        Act: Signup a participant, verify in list, remove, verify removed.
        Assert: Verify all state changes are reflected correctly.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "workflow_tester@mergington.edu"
        
        # Act 1: Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act 2: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup worked
        assert signup_response.status_code == 200
        after_signup = client.get("/activities").json()
        assert len(after_signup[activity_name]["participants"]) == initial_count + 1
        assert email in after_signup[activity_name]["participants"]
        
        # Act 3: Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert removal worked
        assert remove_response.status_code == 200
        after_removal = client.get("/activities").json()
        assert len(after_removal[activity_name]["participants"]) == initial_count
        assert email not in after_removal[activity_name]["participants"]

    def test_activities_isolated_between_classes(self, client):
        """
        Arrange: Have multiple activities.
        Act: Signup to one activity and remove from another.
        Assert: Verify changes only affect intended activity.
        """
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        email = "isolation_tester@mergington.edu"
        
        # Act - Sign up to activity1
        client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        
        # Assert - activity2 unchanged
        response = client.get("/activities")
        activities_data = response.json()
        assert email not in activities_data[activity2]["participants"]
        assert email in activities_data[activity1]["participants"]
