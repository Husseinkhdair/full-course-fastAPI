import pytest
from sqlalchemy.orm import Session
from Core.DataBase.PostgresDB import engine
from Core.errors.AuthErrors import UserAlredyExists
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Data.Models.AuthModelPostgres import Base
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase


@pytest.fixture
def db_session():
    # 1. التأكد من إنشاء الجداول في قاعدة بيانات Postgres
    Base.metadata.create_all(bind=engine)

    # 2. فتح Connection وبدء Transaction رئيسية
    connection = engine.connect()
    transaction = connection.begin()

    # 3. إنشاء Session مع create_savepoint لاعتراض الـ commit الداخلي
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    # 4. ينفذ دائماً عند انتهاء الاختبار (نجاح أو فشل) للتراجع عن كافة العمليات
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def auth_repository(db_session: Session) -> AuthRepository:
    return AuthRepositoryPostgresSQl(db=db_session)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_create_user_success(create_user_usecase: CreateUserUseCase):
    email = "pg_rollback_success@test.com"
    name = "Postgres User"
    password = "password123"

    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password
    )

    assert user is not None
    assert isinstance(user, UserEntity)
    assert user.email == email
    assert user.name == name
    assert user.token is not None
    assert user.id is not None


@pytest.mark.asyncio
async def test_create_user_already_exists(create_user_usecase: CreateUserUseCase):
    email = "pg_rollback_duplicate@test.com"
    name = "Duplicate User"
    password = "password123"

    # إنشاء المستخدم لأول مرة
    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password
    )
    assert user is not None

    # محاولة إنشاء نفس المستخدم مرة ثانية يجب أن ترمي خطأ UserAlredyExists
    with pytest.raises(UserAlredyExists):
        await create_user_usecase.execute(
            email=email,
            name=name,
            password=password
        )
