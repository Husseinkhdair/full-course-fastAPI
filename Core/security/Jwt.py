from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt

from Core.Settings import SettingsApp

settings = SettingsApp()


class JWTPayload:
    def __init__(
        self,
        sub: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
        exp: Optional[int] = None,
        iat: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.sub = sub
        self.email = email
        self.role = role
        self.exp = exp
        self.iat = iat
        self.extra = extra or {}

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "sub": str(self.sub),
        }
        if self.email is not None:
            data["email"] = self.email
        if self.role is not None:
            data["role"] = str(self.role)
        if self.exp is not None:
            data["exp"] = self.exp
        if self.iat is not None:
            data["iat"] = self.iat

        for k, v in self.extra.items():
            if k not in data:
                data[k] = v

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JWTPayload":
        if not data:
            return None
        data_copy = dict(data)
        sub = str(data_copy.pop("sub", ""))
        email = data_copy.pop("email", None)
        role = data_copy.pop("role", None)
        exp = data_copy.pop("exp", None)
        iat = data_copy.pop("iat", None)

        return cls(
            sub=sub,
            email=email,
            role=role,
            exp=exp,
            iat=iat,
            extra=data_copy,
        )

    def __repr__(self):
        return f"JWTPayload(sub={self.sub}, email={self.email}, role={self.role}, exp={self.exp}, iat={self.iat}, extra={self.extra})"


def generate_token(
    payload: JWTPayload,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    key = secret_key or settings.secret_key
    algo = algorithm or settings.jwt_algorithm
    payload_dict = payload.to_dict()

    now = datetime.now(timezone.utc)
    if "iat" not in payload_dict or payload_dict["iat"] is None:
        payload_dict["iat"] = int(now.timestamp())

    if "exp" not in payload_dict or payload_dict["exp"] is None:
        delta = expires_delta if expires_delta is not None else timedelta(minutes=settings.access_token_expire_minutes)
        payload_dict["exp"] = int((now + delta).timestamp())

    return jwt.encode(payload_dict, key, algorithm=algo)


def verify_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> Optional[JWTPayload]:
    key = secret_key or settings.secret_key
    algo = algorithm or settings.jwt_algorithm
    try:
        decoded = jwt.decode(token, key, algorithms=[algo])
        return JWTPayload.from_dict(decoded)
    except (jwt.PyJWTError, Exception):
        return None
