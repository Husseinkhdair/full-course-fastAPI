from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from Core.di import (
    get_current_token,
    get_create_post_usecase,
    get_update_post_usecase,
    get_delete_post_usecase,
    get_post_by_id_usecase,
    get_list_posts_usecase,
)
from Features.Post.Domain.UseCases import (
    CreatePostUseCase,
    UpdatePostUseCase,
    DeletePostUseCase,
    GetPostByIdUseCase,
    ListPostsUseCase,
)
from Features.Post.Presentation.tdo import CreatePostTDO, InfoPostTDO, UpdatePostTDO

router = APIRouter(prefix="/post", tags=["Post"])


@router.post("", response_model=InfoPostTDO, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: CreatePostTDO,
    token: str = Depends(get_current_token),
    usecase: CreatePostUseCase = Depends(get_create_post_usecase),
):
    entity = await usecase.execute(
        title=post_data.title,
        content=post_data.content,
        token=token,
    )
    return InfoPostTDO.from_entity(entity)


@router.get("/{post_id}", response_model=InfoPostTDO, status_code=status.HTTP_200_OK)
async def get_post_by_id(
    post_id: str,
    usecase: GetPostByIdUseCase = Depends(get_post_by_id_usecase),
):
    entity = await usecase.execute(post_id=post_id)
    return InfoPostTDO.from_entity(entity)


@router.get("", response_model=List[InfoPostTDO], status_code=status.HTTP_200_OK)
async def list_posts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    usecase: ListPostsUseCase = Depends(get_list_posts_usecase),
):
    entities = await usecase.execute(limit=limit, offset=offset)
    return [InfoPostTDO.from_entity(e) for e in entities]


@router.put("/{post_id}", response_model=InfoPostTDO, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: str,
    post_data: UpdatePostTDO,
    token: str = Depends(get_current_token),
    usecase: UpdatePostUseCase = Depends(get_update_post_usecase),
):
    entity = await usecase.execute(
        post_id=post_id,
        title=post_data.title,
        content=post_data.content,
        token=token,
    )
    return InfoPostTDO.from_entity(entity)


@router.delete("/{post_id}", response_model=bool, status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: str,
    token: str = Depends(get_current_token),
    usecase: DeletePostUseCase = Depends(get_delete_post_usecase),
):
    return await usecase.execute(post_id=post_id, token=token)
