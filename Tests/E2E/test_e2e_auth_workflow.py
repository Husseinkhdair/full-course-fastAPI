import uuid
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_complete_e2e_user_workflow():
    # Generate unique test user credentials
    unique_suffix = str(uuid.uuid4())[:8]
    test_email = f"e2e_user_{unique_suffix}@example.com"
    test_password = "Pass123456"

    test_name = f"E2E User {unique_suffix}"

    # ----------------------------------------------------
    # Step 1: Check root health endpoint
    # ----------------------------------------------------
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.json() == {"Hello": "World"}
    assert "x-request-id" in root_res.headers

    # ----------------------------------------------------
    # Step 2: Register a new user
    # ----------------------------------------------------
    register_payload = {
        "name": test_name,
        "email": test_email,
        "password": test_password
    }
    reg_res = client.post("/auth/register", json=register_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()

    assert reg_data["email"] == test_email
    assert reg_data["name"] == test_name
    assert reg_data["role"] == "user"
    assert reg_data["status"] == "active"
    assert "user_id" in reg_data
    assert reg_data["user_id"] is not None
    user_id = str(reg_data["user_id"])

    # ----------------------------------------------------
    # Step 3: Attempt duplicate registration (should fail with 400)
    # ----------------------------------------------------
    dup_res = client.post("/auth/register", json=register_payload)
    assert dup_res.status_code == 400
    assert dup_res.json()["detail"] == "User alredy exists"

    # ----------------------------------------------------
    # Step 4: Login with incorrect password (should fail with 401)
    # ----------------------------------------------------
    bad_login_res = client.post("/auth/login", json={
        "email": test_email,
        "password": "WrongPassword!"
    })
    assert bad_login_res.status_code == 401
    assert bad_login_res.json()["detail"] == "Invalid email or password"

    # ----------------------------------------------------
    # Step 5: Login with correct password (should succeed with 200)
    # ----------------------------------------------------
    login_res = client.post("/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["email"] == test_email
    assert str(login_data["user_id"]) == user_id

    # ----------------------------------------------------
    # Step 6: Query user profile by Email
    # ----------------------------------------------------
    get_email_res = client.get(f"/auth/user/email/{test_email}")
    assert get_email_res.status_code == 200
    email_data = get_email_res.json()
    assert email_data["email"] == test_email
    assert str(email_data["user_id"]) == user_id

    # ----------------------------------------------------
    # Step 7: Query user profile by User ID
    # ----------------------------------------------------
    get_id_res = client.get(f"/auth/user/id/{user_id}")
    assert get_id_res.status_code == 200
    id_data = get_id_res.json()
    assert id_data["email"] == test_email
    assert id_data["name"] == test_name

    # ----------------------------------------------------
    # Step 8: Query non-existent user profile by Email (should fail with 400)
    # ----------------------------------------------------
    non_existent_email_res = client.get("/auth/user/email/nonexistent9999@example.com")
    assert non_existent_email_res.status_code == 400
    assert non_existent_email_res.json()["detail"] == "User does not exists"

    # ----------------------------------------------------
    # Step 9: Query non-existent user profile by ID (should fail with 400)
    # ----------------------------------------------------
    non_existent_id_res = client.get("/auth/user/id/nonexistent_id_9999")
    assert non_existent_id_res.status_code == 400
    assert non_existent_id_res.json()["detail"] == "User does not exists"

    # ----------------------------------------------------
    # Step 10: Delete user by User ID (should succeed with boolean True)
    # ----------------------------------------------------
    delete_res = client.delete(f"/auth/user/id/{user_id}")
    assert delete_res.status_code == 200
    assert delete_res.json() is True

    # Verify user no longer exists after deletion
    post_delete_res = client.get(f"/auth/user/id/{user_id}")
    assert post_delete_res.status_code == 400
    assert post_delete_res.json()["detail"] == "User does not exists"

