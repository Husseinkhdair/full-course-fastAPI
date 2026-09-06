from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
# from Features.Auth.Data.Models.AuthModelMongos import AuthMongosModel
# from Features.Auth.Data.Models.AuthModelPostgres import AuthPostgresModel



from Core.Strings import RoleString
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