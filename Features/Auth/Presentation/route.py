from fastapi import APIRouter, Depends, status
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase,
    DeleteUserUseCase
)
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO
from Core.di import (
    get_create_user_usecase,
    get_login_user_usecase,
    get_user_by_id_usecase,
    get_user_by_email_usecase,
    get_delete_user_usecase
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=InfoUserTDO, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: CreateUserTDO,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase)
):
    return await usecase.execute(user)


@router.post("/login", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def login_user(
    user: LoginTDO,
    usecase: LoginUserUseCase = Depends(get_login_user_usecase)
):
    return await usecase.execute(user)


@router.get("/user/id/{user_id}", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: str,
    usecase: GetUserByIdUseCase = Depends(get_user_by_id_usecase)
):
    return await usecase.execute(user_id)


@router.get("/user/email/{email}", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def get_user_by_email(
    email: str,
    usecase: GetUserByEmailUseCase = Depends(get_user_by_email_usecase)
):
    return await usecase.execute(email)


@router.delete("/user/id/{user_id}", response_model=bool, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    usecase: DeleteUserUseCase = Depends(get_delete_user_usecase)
):
    return await usecase.execute(user_id)


