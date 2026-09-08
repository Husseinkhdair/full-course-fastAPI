from abc import ABC, abstractmethod
from typing import List, Optional
from Features.Post.Domain.Entities.PostEntity import PostEntity


class PostRepository(ABC):
    @abstractmethod
    async def create_post(self, post: PostEntity) -> PostEntity:
        pass

    @abstractmethod
    async def update_post(self, post: PostEntity) -> PostEntity:
        pass

    @abstractmethod
    async def get_post_by_id(self, post_id: str) -> PostEntity:
        pass

    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        pass

    @abstractmethod
    async def list_posts(self, limit: int = 10, offset: int = 0) -> List[PostEntity]:
        pass

    @abstractmethod
    async def delete_posts_by_author_id(self, author_id: str) -> int:
        pass
