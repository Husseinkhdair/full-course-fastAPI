import pytest
from fastapi.testclient import TestClient

from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
from Features.Auth.Presentation.tdo import CreateUserTDO, InfoUserTDO, LoginTDO
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.integration
def test_tdo_models_and_entity_conversion():
    create_tdo = CreateUserTDO(
        name="Integration User",
        email="integ_tdo@example.com",
        password="password123",
    )
    assert create_tdo.name == "Integration User"
    assert create_tdo.email == "integ_tdo@example.com"

    login_tdo = LoginTDO(email="integ_tdo@example.com", password="password123")
    assert login_tdo.email == "integ_tdo@example.com"

    entity = UserEntity(
        id="integ_id_123",
        name="Integration User",
        email="integ_tdo@example.com",
        password="hashed_password",
        role=Role.USER,
        status=Status.ACTIVE,
    )
    entity.token = "sample_jwt_token_123"

    info_tdo = InfoUserTDO.from_entity(entity)
    assert info_tdo.user_id == "integ_id_123"
    assert info_tdo.name == "Integration User"
    assert info_tdo.email == "integ_tdo@example.com"
    assert info_tdo.role == "user"
    assert info_tdo.status == "active"
    assert info_tdo.token == "sample_jwt_token_123"


@pytest.mark.integration
def test_full_auth_routes_integration_flow(client: TestClient):
    email = "full_flow_user@test.com"
    name = "Full Flow"
    password = "password123"

    # 1. Register User via POST /auth/register
    reg_response = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["email"] == email
    assert reg_data["name"] == name
    assert "user_id" in reg_data
    assert "token" in reg_data
    assert reg_data["token"] is not None

    user_id = str(reg_data["user_id"])

    # 2. Login User via POST /auth/login
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["user_id"] == user_id
    assert login_data["email"] == email
    assert login_data["token"] is not None

    # 3. Get User By ID via GET /auth/user/id/{user_id} (Requires Admin Token)
    from Core.security.Jwt import JWTPayload, generate_token
    admin_token = generate_token(JWTPayload(id="admin_id", role="admin"))
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    get_id_response = client.get(f"/auth/user/id/{user_id}", headers=auth_headers)
    assert get_id_response.status_code == 200
    get_id_data = get_id_response.json()
    assert get_id_data["user_id"] == user_id
    assert get_id_data["email"] == email

    # 4. Get User By Email via GET /auth/user/email/{email} (Requires Admin Token)
    get_email_response = client.get(f"/auth/user/email/{email}", headers=auth_headers)
    assert get_email_response.status_code == 200
    get_email_data = get_email_response.json()
    assert get_email_data["user_id"] == user_id
    assert get_email_data["email"] == email

    # 5. Delete User via DELETE /auth/user/id/{user_id} (Requires Admin Token)
    del_response = client.delete(f"/auth/user/id/{user_id}", headers=auth_headers)
    assert del_response.status_code == 200
    assert del_response.json() is True


@pytest.mark.integration
def test_register_already_exists_route_integration(client: TestClient):
    email = "dup_route_user@test.com"
    name = "Duplicate Route User"
    password = "password123"

    reg1 = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg1.status_code == 201
    user_id = str(reg1.json()["user_id"])

    # Duplicate registration should return error status
    reg2 = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg2.status_code in (400, 409, 500, 401)

    # Cleanup (Requires Admin Token)
    from Core.security.Jwt import JWTPayload, generate_token
    admin_token = generate_token(JWTPayload(id="admin_cleanup", role="admin"))
    auth_headers = {"Authorization": f"Bearer {admin_token}"}
    client.delete(f"/auth/user/id/{user_id}", headers=auth_headers)


@pytest.mark.integration
def test_login_invalid_password_route_integration(client: TestClient):
    email = "invalid_pwd_route@test.com"
    name = "Invalid Password User"
    password = "password123"

    reg = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg.status_code == 201
    user_id = str(reg.json()["user_id"])

    # Login with wrong password should fail
    login_fail = client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )
    assert login_fail.status_code in (401, 400, 500)

    # Cleanup (Requires Admin Token)
    from Core.security.Jwt import JWTPayload, generate_token
    admin_token = generate_token(JWTPayload(id="admin_cleanup_2", role="admin"))
    auth_headers = {"Authorization": f"Bearer {admin_token}"}
    client.delete(f"/auth/user/id/{user_id}", headers=auth_headers)
