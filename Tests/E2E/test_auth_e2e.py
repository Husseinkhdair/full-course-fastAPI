import pytest
from fastapi.testclient import TestClient

from Core.security.Jwt import verify_token
from main import app


@pytest.fixture
def e2e_client():
    return TestClient(app)


@pytest.mark.e2e
def test_e2e_complete_user_lifecycle(e2e_client: TestClient):
    email = "e2e_user_lifecycle@example.com"
    name = "E2E Lifecycle User"
    password = "password123"

    # Step 1: Register User
    reg_res = e2e_client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()

    assert reg_data["email"] == email
    assert reg_data["name"] == name
    assert "user_id" in reg_data
    assert "token" in reg_data
    assert reg_data["token"] is not None

    user_id = str(reg_data["user_id"])
    register_token = reg_data["token"]

    # Step 2: Validate JWT Token from Registration
    token_payload = verify_token(register_token)
    assert token_payload is not None
    assert token_payload.id == user_id
    assert token_payload.email == email

    # Step 3: Login User
    login_res = e2e_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()

    assert login_data["user_id"] == user_id
    assert login_data["email"] == email
    login_token = login_data["token"]
    assert login_token is not None

    # Step 4: Validate JWT Token from Login
    login_payload = verify_token(login_token)
    assert login_payload is not None
    assert login_payload.id == user_id

    # Step 5: Fetch Profile by User ID
    get_id_res = e2e_client.get(f"/auth/user/id/{user_id}")
    assert get_id_res.status_code == 200
    get_id_data = get_id_res.json()
    assert get_id_data["user_id"] == user_id
    assert get_id_data["email"] == email

    # Step 6: Fetch Profile by Email
    get_email_res = e2e_client.get(f"/auth/user/email/{email}")
    assert get_email_res.status_code == 200
    get_email_data = get_email_res.json()
    assert get_email_data["user_id"] == user_id
    assert get_email_data["email"] == email

    # Step 7: Delete User Account
    del_res = e2e_client.delete(f"/auth/user/id/{user_id}")
    assert del_res.status_code == 200
    assert del_res.json() is True

    # Step 8: Verify Login Fails After Account Deletion
    post_del_login = e2e_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert post_del_login.status_code in (401, 400, 500)


@pytest.mark.e2e
def test_e2e_multiple_users_isolation(e2e_client: TestClient):
    user1_email = "e2e_user1@example.com"
    user2_email = "e2e_user2@example.com"
    password = "password123"

    # Register User 1
    res1 = e2e_client.post(
        "/auth/register",
        json={"name": "User One", "email": user1_email, "password": password},
    )
    assert res1.status_code == 201
    user1_id = str(res1.json()["user_id"])

    # Register User 2
    res2 = e2e_client.post(
        "/auth/register",
        json={"name": "User Two", "email": user2_email, "password": password},
    )
    assert res2.status_code == 201
    user2_id = str(res2.json()["user_id"])

    assert user1_id != user2_id

    # Fetch User 1 and User 2 profiles and verify separation
    p1 = e2e_client.get(f"/auth/user/id/{user1_id}").json()
    p2 = e2e_client.get(f"/auth/user/id/{user2_id}").json()

    assert p1["email"] == user1_email
    assert p2["email"] == user2_email

    # Cleanup
    e2e_client.delete(f"/auth/user/id/{user1_id}")
    e2e_client.delete(f"/auth/user/id/{user2_id}")


@pytest.mark.e2e
def test_e2e_invalid_registration_data(e2e_client: TestClient):
    # Invalid Email format
    res_bad_email = e2e_client.post(
        "/auth/register",
        json={"name": "Bad Email", "email": "not-an-email", "password": "password123"},
    )
    assert res_bad_email.status_code == 422

    # Password too short (less than 6 chars per CreateUserTDO)
    res_short_pwd = e2e_client.post(
        "/auth/register",
        json={"name": "Short Pwd", "email": "valid@example.com", "password": "123"},
    )
    assert res_short_pwd.status_code == 422
