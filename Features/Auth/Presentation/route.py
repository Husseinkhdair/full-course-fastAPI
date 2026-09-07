from fastapi import APIRouter, Depends, status, Response
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase,
    DeleteUserUseCase
)
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO
from Core.Settings import SettingsApp
from Core.di import (
    get_create_user_usecase,
    get_login_user_usecase,
    get_user_by_id_usecase,
    get_user_by_email_usecase,
    get_delete_user_usecase
)

settings = SettingsApp()
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=InfoUserTDO, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: CreateUserTDO,
    response: Response,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase)
):
    user_entity = await usecase.execute(email=user.email, name=user.name, password=user.password)
    
    if getattr(user_entity, "token", None):
        max_age = settings.access_token_expire_minutes * 60 if settings.access_token_expire_minutes else None
        response.set_cookie(
            key="access_token",
            value=user_entity.token,
            httponly=True,
            samesite="lax",
            secure=settings.Development == "False",
            max_age=max_age
        )
    
    return InfoUserTDO.from_entity(user_entity)


@router.post("/login", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def login_user(
    user: LoginTDO,
    response: Response,
    usecase: LoginUserUseCase = Depends(get_login_user_usecase)
):
    user_entity = await usecase.execute(email=user.email, password=user.password)
    
    if getattr(user_entity, "token", None):
        max_age = settings.access_token_expire_minutes * 60 if settings.access_token_expire_minutes else None
        response.set_cookie(
            key="access_token",
            value=user_entity.token,
            httponly=True,
            samesite="lax",
            secure=settings.Development == "False",
            max_age=max_age
        )
    
    return InfoUserTDO.from_entity(user_entity)


@router.get("/user/id/{user_id}", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: str,
    usecase: GetUserByIdUseCase = Depends(get_user_by_id_usecase)
):
    user_entity = await usecase.execute(user_id)
    return InfoUserTDO.from_entity(user_entity)


@router.get("/user/email/{email}", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def get_user_by_email(
    email: str,
    usecase: GetUserByEmailUseCase = Depends(get_user_by_email_usecase)
):
    user_entity = await usecase.execute(email)
    return InfoUserTDO.from_entity(user_entity)


@router.delete("/user/id/{user_id}", response_model=bool, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    usecase: DeleteUserUseCase = Depends(get_delete_user_usecase)
):
    return await usecase.execute(user_id)



