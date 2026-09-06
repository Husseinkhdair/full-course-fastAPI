from fastapi import HTTPException

class AuthError(HTTPException):
    def __init__(self,detail:str,status_code:int):
        super().__init__(status_code,detail)


class UserAlredyExists(AuthError):
    def __init__(self):
        super().__init__("User alredy exists",400)

class UserDoesNotExists(AuthError):
    def __init__(self):
        super().__init__("User does not exists",400)

class InvalidEmailOrPassword(AuthError):
    def __init__(self):
        super().__init__("Invalid email or password",401)

class UserNotHaveRole(AuthError):
    def __init__(self):
        super().__init__("User not have role",403)

class InvalidToken(AuthError):
    def __init__(self):
        super().__init__("Invalid token",401)