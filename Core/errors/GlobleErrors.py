from fastapi import HTTPException
from Core.Settings import SettingsApp

class GlobleErrors(HTTPException):
    def __init__(self,detail:str,status_code:int):
        super().__init__(status_code,detail)


class ServerError(GlobleErrors):
    def __init__(self,detail:str="Server error"):
        if SettingsApp().Development == "False":
            detail = "Server error"
        super().__init__(detail,500)
    