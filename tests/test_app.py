import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        copy.deepcopy(app_module.activities),
    )
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_adds_participant(client):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Art Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Art Club"]["participants"]


def test_duplicate_signup_is_rejected(client):
    email = "student@mergington.edu"
    signup_url = "/activities/Art Club/signup"

    assert client.post(signup_url, params={"email": email}).status_code == 200
    response = client.post(signup_url, params={"email": email})

    assert response.status_code == 400
    assert client.get("/activities").json()["Art Club"]["participants"].count(email) == 1


def test_signup_for_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_remove_participant(client):
    email = "student@mergington.edu"
    client.post("/activities/Art Club/signup", params={"email": email})

    response = client.delete(
        "/activities/Art Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Art Club"]["participants"]


def test_remove_unregistered_participant_returns_not_found(client):
    response = client.delete(
        "/activities/Art Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
