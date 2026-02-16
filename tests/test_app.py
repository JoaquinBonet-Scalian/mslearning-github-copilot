import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    # Add more assertions based on your root endpoint's response

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307 or response.status_code == 302
    assert "/static/index.html" in response.headers["location"]


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Soccer Team" in data
    assert "participants" in data["Soccer Team"]


def test_signup_success():
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    # Ensure user is not already signed up
    client.delete(f"/activities/{activity}/signup", params={"email": email})
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Clean up
    client.delete(f"/activities/{activity}/signup", params={"email": email})


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "foo@bar.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_signed_up():
    activity = "Soccer Team"
    email = "alex@mergington.edu"
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_full():
    activity = "Chess Club"
    # Fill up the activity
    for i in range(12):
        email = f"fulluser{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})
    # Now try to add one more
    response = client.post(f"/activities/{activity}/signup", params={"email": "overflow@mergington.edu"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    # Clean up
    for i in range(12):
        email = f"fulluser{i}@mergington.edu"
        client.delete(f"/activities/{activity}/signup", params={"email": email})


def test_remove_participant_success():
    activity = "Art Studio"
    email = "removeuser@mergington.edu"
    # Add user first
    client.post(f"/activities/{activity}/signup", params={"email": email})
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert f"Removed {email} from {activity}" in response.json()["message"]


def test_remove_participant_not_found():
    activity = "Art Studio"
    email = "notfound@mergington.edu"
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_remove_participant_activity_not_found():
    response = client.delete("/activities/Nonexistent/signup", params={"email": "foo@bar.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
