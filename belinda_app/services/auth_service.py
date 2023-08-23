import hmac
import hashlib
import base64
import json

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from belinda_app.models import Musician, UserSession
from belinda_app.settings import get_settings
from belinda_app.db.database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()

SECRET_KEY = settings.SESSION_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


async def verify_password(plain_password, hashed_password):
    password_bytes = plain_password.encode('utf-8')
    expected_hash = hmac.new(SECRET_KEY.encode('utf-8'), password_bytes, hashlib.sha256)
    expected_hash_digest = expected_hash.digest()
    expected_hash_base64 = base64.urlsafe_b64encode(expected_hash_digest).rstrip(b"=").decode("utf-8")

    return hmac.compare_digest(hashed_password, expected_hash_base64)


def create_access_token(data: dict):
    header = json.dumps({"alg": ALGORITHM, "typ": "JWT"})
    payload = json.dumps(data)

    header_encoded = base64.urlsafe_b64encode(header.encode("utf-8")).rstrip(b"=").decode("utf-8")
    payload_encoded = base64.urlsafe_b64encode(payload.encode("utf-8")).rstrip(b"=").decode("utf-8")

    signature_payload = f"{header_encoded}.{payload_encoded}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signature_payload, hashlib.sha256)
    signature_encoded = base64.urlsafe_b64encode(signature.digest()).rstrip(b"=").decode("utf-8")

    jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
    return jwt_token


async def authenticate_user(login: str, password: str, db: AsyncSession):
    result = await db.execute(select(Musician).where(Musician.login == login))
    musician = result.scalar_one_or_none()

    if musician is None or not pwd_context.verify(password, musician.password):
        return None

    session = UserSession(musician_id=musician.musician_id, access_token=create_access_token({"sub": musician.login}))
    db.add(session)
    await db.commit()

    return musician


async def get_current_musician(
    musician_id: str = Cookie(default=None),
    db: AsyncSession = Depends(get_session)
):
    if musician_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = await db.execute(
        select(UserSession)
        .where(UserSession.musician_id == musician_id)
        .order_by(desc(UserSession.created_at))
        .limit(1)
    )
    user_session = session.scalar_one_or_none()

    if user_session is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {"access_token": user_session.access_token}
