from Core.errors.AuthErrors import InvalidToken
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
import logging
from Core.Settings import SettingsApp

settings = SettingsApp()
logger = logging.getLogger(__name__)

class JWTPayload:
    def __init__(
        self,
        id: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
        exp: Optional[int] = None
        
        
    ):
        self.id = id
        self.email = email
        self.role = role
        self.exp = exp
       
        

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": str(self.id),
        }
        if self.email is not None:
            data["email"] = self.email
        if self.role is not None:
            data["role"] = str(self.role)
        if self.exp is not None:
            data["exp"] = self.exp
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JWTPayload":
        if not data:
            return None
        data_copy = dict(data)
        id = str(data_copy.pop("id", ""))
        email = data_copy.pop("email", None)
        role = data_copy.pop("role", None)
        exp = data_copy.pop("exp", None)

        return cls(
            id=id,
            email=email,
            role=role,
            exp=exp,
           
        )

    def __repr__(self):
        return f"JWTPayload(id={self.id}, email={self.email}, role={self.role}, exp={self.exp})"


def generate_token(
    payload: JWTPayload,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    try:
        key = secret_key or settings.secret_key
        algo = algorithm or settings.jwt_algorithm
        payload_dict = payload.to_dict()

        now = datetime.now(timezone.utc)
        if "exp" not in payload_dict or payload_dict["exp"] is None:
            delta = expires_delta if expires_delta is not None else timedelta(minutes=settings.access_token_expire_minutes)
            payload_dict["exp"] = int((now + delta).timestamp())

        logger.debug("token created successfully")
        return jwt.encode(payload_dict, key, algorithm=algo)
    except (jwt.PyJWTError, Exception) as e:
        logger.exception(f"Error creating token: {payload_dict} : {e}")
        raise InvalidToken()


def verify_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> Optional[JWTPayload]:
    key = secret_key or settings.secret_key
    algo = algorithm or settings.jwt_algorithm
    try:
        decoded = jwt.decode(token, key, algorithms=[algo])
        logger.debug("token verified successfully")
        return JWTPayload.from_dict(decoded)
    except (jwt.PyJWTError, Exception) as e:
        logger.debug(f"Error Invalid token: {token} : {e}")
        raise InvalidToken()
