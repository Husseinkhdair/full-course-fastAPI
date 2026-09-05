from fastapi import APIRouter, status
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase
)
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO

router = APIRouter(prefix="/auth", tags=["Auth"])

# Repository & UseCase instances
auth_repository = AuthRepositoryMongoDB()
create_user_usecase = CreateUserUseCase(auth_repository)
login_user_usecase = LoginUserUseCase(auth_repository)
get_user_by_id_usecase = GetUserByIdUseCase(auth_repository)
get_user_by_email_usecase = GetUserByEmailUseCase(auth_repository)


@router.post("/register", response_model=InfoUserTDO, status_code=status.HTTP_201_CREATED)
async def register_user(user: CreateUserTDO):
    return await create_user_usecase.execute(user)


@router.post("/login", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def login_user(user: LoginTDO):
    return await login_user_usecase.execute(user)


@router.get("/user/id/{user_id}", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str):
    return await get_user_by_id_usecase.execute(user_id)


@router.get("/user/email/{email}", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def get_user_by_email(email: str):
    return await get_user_by_email_usecase.execute(email)
