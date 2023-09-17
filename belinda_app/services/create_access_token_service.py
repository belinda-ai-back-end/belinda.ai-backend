import jwt
import datetime

from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException

from belinda_app.settings import get_settings

settings = get_settings()

SECRET_KEY = settings.SESSION_SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(user_id: str, expires_delta: datetime.timedelta) -> str:
    to_encode = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + expires_delta
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def check_cookie(request: Request):
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Cookie access_token not found")

    return access_token
