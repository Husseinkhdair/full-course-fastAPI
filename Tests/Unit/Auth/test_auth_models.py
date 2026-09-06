from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
from Features.Auth.Data.Models.AuthModelMongos import AuthMongosModel
from Features.Auth.Data.Models.AuthModelPostgres import AuthPostgresModel
from Features.Auth.Domain.Entities.UserEntity import UserEntity




def test_auth_entity_default_values():
    user = UserEntity(name="test", email="test@gmail.com", password="password")

    assert user.role == Role.USER
    assert user.status == Status.ACTIVE
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_auth_entity_custom_values():
    user = UserEntity(name="test", email="test@gmail.com", password="password", role=Role.ADMIN, status=Status.INACTIVE, id="123", created_at="2022-01-01 00:00:00", updated_at="2022-01-01 00:00:00")

    assert user.role == Role.ADMIN
    assert user.status == Status.INACTIVE
    assert user.id == "123"
    assert user.created_at == "2022-01-01 00:00:00"
    assert user.updated_at == "2022-01-01 00:00:00"


def test_model_mongos_default_values():
    user = AuthMongosModel(name="test", email="test@gmail.com", password="password")

    assert user.role == Role.USER
    assert user.status == Status.ACTIVE
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_auth_model_mongos_custom_values():
    user = AuthMongosModel(name="test", email="test@gmail.com", password="password", role=Role.ADMIN, status=Status.INACTIVE, id="123", created_at="2022-01-01 00:00:00", updated_at="2022-01-01 00:00:00")

    assert user.role == Role.ADMIN
    assert user.status == Status.INACTIVE
    assert user.id == "123"
    assert user.created_at == "2022-01-01 00:00:00"
    assert user.updated_at == "2022-01-01 00:00:00"


def test_auth_model_mongos_to_entity():
    user = AuthMongosModel(name="test", email="test@gmail.com", password="password", role=Role.ADMIN, status=Status.INACTIVE, id="123", created_at="2022-01-01 00:00:00", updated_at="2022-01-01 00:00:00")
    entity = user.to_entity()

    assert entity.name == "test"
    assert entity.email == "test@gmail.com"
    assert entity.password == "password"
    assert entity.role == Role.ADMIN
    assert entity.status == Status.INACTIVE
    assert entity.id == "123"
    assert entity.created_at == "2022-01-01 00:00:00"
    assert entity.updated_at == "2022-01-01 00:00:00"
    assert isinstance(entity, UserEntity)
    

def test_auth_model_mongos_from_entity():
    entity = UserEntity(name="test", email="test@gmail.com", password="password", role=Role.ADMIN, status=Status.INACTIVE, id="123", created_at="2022-01-01 00:00:00", updated_at="2022-01-01 00:00:00")
    user = AuthMongosModel.from_entity(entity)

    assert user.name == "test"
    assert user.email == "test@gmail.com"
    assert user.password == "password"
    assert user.role == Role.ADMIN
    assert user.status == Status.INACTIVE
    assert user.id == "123"
    assert user.created_at == "2022-01-01 00:00:00"
    assert user.updated_at == "2022-01-01 00:00:00"
    assert isinstance(user, AuthMongosModel)



def test_auth_model_postgres_default_values():
    user = AuthPostgresModel(name="test", email="test@gmail.com", password="password")
    assert user.name == "test"
    assert user.email == "test@gmail.com"
    assert user.password == "password"
    assert user.role == Role.USER
    assert user.status == Status.ACTIVE
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_auth_model_mongos_to_dict():
    user = AuthMongosModel(
        name="test",
        email="test@gmail.com",
        password="password",
        role=Role.ADMIN,
        status=Status.INACTIVE,
        id="123",
        created_at="2022-01-01 00:00:00",
        updated_at="2022-01-01 00:00:00"
        )


    user_dict = user.to_dict()

    assert user_dict["_id"] == "123"
    assert user_dict["name"] == "test"
    assert user_dict["email"] == "test@gmail.com"
    assert user_dict["password"] == "password"
    assert user_dict["role"] == "admin"
    assert user_dict["status"] == "inactive"
    assert user_dict["created_at"] == "2022-01-01 00:00:00"
    assert user_dict["updated_at"] == "2022-01-01 00:00:00"
    assert isinstance(user_dict, dict)


def test_auth_model_mongos_from_dict():
    user_dict = {
        "_id": "123",
        "name": "test",
        "email": "test@gmail.com",
        "password": "password",
        "role": Role.ADMIN,
        "status": Status.INACTIVE,
        "created_at": "2022-01-01 00:00:00",
        "updated_at": "2022-01-01 00:00:00"
        }

    user = AuthMongosModel.from_dict(user_dict)

    assert user.id == "123"
    assert user.name == "test"
    assert user.email == "test@gmail.com"
    assert user.password == "password"
    assert user.role == Role.ADMIN
    assert user.status == Status.INACTIVE
    assert user.created_at == "2022-01-01 00:00:00"
    assert user.updated_at == "2022-01-01 00:00:00"
    assert isinstance(user, AuthMongosModel)


def test_auth_model_postgres_custom_values():
    user = AuthPostgresModel(
        name="test",
        email="test@gmail.com",
        password="password",
        role=Role.ADMIN,
        status=Status.INACTIVE,
        id="123",
        created_at="2022-01-01 00:00:00",
        updated_at="2022-01-01 00:00:00",
    )

    assert user.role == Role.ADMIN
    assert user.status == Status.INACTIVE
    assert user.id == "123"
    assert user.created_at == "2022-01-01 00:00:00"
    assert user.updated_at == "2022-01-01 00:00:00"


def test_auth_model_postgres_to_entity():
    user = AuthPostgresModel(
        name="test",
        email="test@gmail.com",
        password="password",
        role=Role.ADMIN,
        status=Status.INACTIVE,
        id="123",
        created_at="2022-01-01 00:00:00",
        updated_at="2022-01-01 00:00:00",
    )
    entity = user.to_entity()

    assert entity.name == "test"
    assert entity.email == "test@gmail.com"
    assert entity.password == "password"
    assert entity.role == Role.ADMIN
    assert entity.status == Status.INACTIVE
    assert entity.id == "123"
    assert entity.created_at == "2022-01-01 00:00:00"
    assert entity.updated_at == "2022-01-01 00:00:00"
    assert isinstance(entity, UserEntity)


def test_auth_model_postgres_from_entity():
    entity = UserEntity(
        name="test",
        email="test@gmail.com",
        password="password",
        role=Role.ADMIN,
        status=Status.INACTIVE,
        id="123",
        created_at="2022-01-01 00:00:00",
        updated_at="2022-01-01 00:00:00",
    )
    user = AuthPostgresModel.from_entity(entity)

    assert user.name == "test"
    assert user.email == "test@gmail.com"
    assert user.password == "password"
    assert user.role in ("admin", Role.ADMIN)
    assert user.status in ("inactive", Status.INACTIVE)
    assert user.id == "123"
    assert user.created_at == "2022-01-01 00:00:00"
    assert user.updated_at == "2022-01-01 00:00:00"
    assert isinstance(user, AuthPostgresModel)