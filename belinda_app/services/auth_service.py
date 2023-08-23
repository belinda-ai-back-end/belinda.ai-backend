import hmac
import hashlib
import base64
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from belinda_app.models import Musician
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
    musician = await db.execute(select(Musician).where(Musician.login == login))
    musician = musician.fetchone()

    if not musician or not verify_password(password, musician.password):
        return None

    return musician


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    try:
        token_parts = token.split(".")
        if len(token_parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")

        header, payload, provided_signature = token_parts
        signature_payload = f"{header}.{payload}".encode("utf-8")
        expected_signature = hmac.new(SECRET_KEY.encode("utf-8"), signature_payload, hashlib.sha256)
        expected_signature_encoded = base64.urlsafe_b64encode(expected_signature.digest()).rstrip(b"=").decode("utf-8")

        if not hmac.compare_digest(provided_signature, expected_signature_encoded):
            raise HTTPException(status_code=401, detail="Invalid token signature")

        payload_data = json.loads(base64.urlsafe_b64decode(payload + "==="))
        login = payload_data.get("sub")
        if login is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.execute(select(Musician).where(Musician.login == login))
    user = user.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
