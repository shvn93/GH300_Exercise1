"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient instance for making requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset the in-memory activities database before each test.
    This ensures tests don't interfere with each other.
    """
    # Save original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current activities and restore original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(original_activities)
