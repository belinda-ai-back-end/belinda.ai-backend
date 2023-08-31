import jwt
import datetime

from fastapi.security import OAuth2PasswordBearer

from belinda_app.settings import get_settings

settings = get_settings()

SECRET_KEY = settings.SESSION_SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(user_id: str, expires_delta: datetime.timedelta) -> str:
    to_encode = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + expires_delta
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
