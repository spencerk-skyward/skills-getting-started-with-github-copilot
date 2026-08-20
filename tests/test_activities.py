from src.app import activities


def test_root_redirects_to_frontend(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Basketball Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up newstudent@mergington.edu for Basketball Club"
    }
    assert "newstudent@mergington.edu" in activities["Basketball Club"]["participants"]


def test_signup_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_is_rejected(client):
    email = "student@mergington.edu"
    endpoint = "/activities/Chess Club/signup"

    first_response = client.post(endpoint, params={"email": email})
    duplicate_response = client.post(endpoint, params={"email": email})

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == (
        "Student already signed up for this activity"
    )
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_at_capacity_is_rejected(client):
    activity = activities["Art Club"]
    activity["participants"] = [f"student{index}@mergington.edu" for index in range(activity["max_participants"])]

    response = client.post(
        "/activities/Art Club/signup",
        params={"email": "overflow@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    assert len(activity["participants"]) == activity["max_participants"]


def test_unregister_removes_participant(client):
    email = "student@mergington.edu"
    client.post("/activities/Chess Club/signup", params={"email": email})

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity_returns_not_found(client):
    response = client.delete(
        "/activities/Unknown Club/participants/student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unknown_participant_returns_not_found(client):
    response = client.delete(
        "/activities/Chess Club/participants/notregistered@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"