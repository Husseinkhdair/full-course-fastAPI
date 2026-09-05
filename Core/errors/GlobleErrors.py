from fastapi import HTTPException

class GlobleErrors(HTTPException):
    def __init__(self,detail:str,status_code:int):
        super().__init__(status_code,detail)


class ServerError(GlobleErrors):
    def __init__(self,detail:str="Server error"):
        super().__init__(detail,500)
    