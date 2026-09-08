from fastapi import HTTPException


class PostError(HTTPException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(status_code=status_code, detail=detail)


class PostNotFound(PostError):
    def __init__(self):
        super().__init__(detail="Post not found", status_code=404)


class PostPermissionDenied(PostError):
    def __init__(self, detail: str = "You do not have permission to modify or delete this post"):
        super().__init__(detail=detail, status_code=403)
