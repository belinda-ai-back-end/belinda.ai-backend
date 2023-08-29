import hmac
import hashlib
import base64
import json
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from belinda_app.models import Musician, UserSession, UserRoleEnum, Curator
from belinda_app.settings import get_settings
from belinda_app.db.database import get_session
from belinda_app.schemas import CreateMusicianRequest, CreateCuratorRequest

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()

SECRET_KEY = settings.SESSION_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


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


def decode_access_token(token: str) -> dict:
    header_encoded, payload_encoded, signature_encoded = token.split(".")
    header = json.loads(base64.urlsafe_b64decode(header_encoded + "==="))
    payload = json.loads(base64.urlsafe_b64decode(payload_encoded + "==="))
    return payload


async def authenticate_user(login: str, password: str, db: AsyncSession):
    result = await db.execute(select(Musician).where(Musician.login == login))
    musician = result.scalar_one_or_none()

    if musician is None or not pwd_context.verify(password, musician.password):
        return None

    session = UserSession(musician_id=musician.musician_id, access_token=create_access_token({"sub": musician.login}))
    db.add(session)
    await db.commit()

    return musician


async def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_session)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="The user is not authenticated")

    payload = decode_access_token(access_token)
    user_id = payload.get("sub")
    user_role = payload.get("user_role")

    if user_id is None or user_role is None:
        raise HTTPException(status_code=401, detail="Invalid access token")

    if user_role == UserRoleEnum.musician:
        session = await db.execute(
            select(UserSession)
            .where(UserSession.musician_id == user_id)
            .order_by(desc(UserSession.created_at))
            .limit(1)
        )
    elif user_role == UserRoleEnum.curator:
        session = await db.execute(
            select(UserSession)
            .where(UserSession.curator_id == user_id)
            .order_by(desc(UserSession.created_at))
            .limit(1)
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid user role")

    user_session = session.scalar_one_or_none()

    if user_session is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {"access_token": user_session.access_token}


async def register_musician(session: AsyncSession, user_data: CreateMusicianRequest):
    hashed_password = pwd_context.hash(user_data.password)
    user_data.password = hashed_password
    user = Musician(**user_data.dict())
    session.add(user)
    await session.commit()
    return user


async def register_curator(session: AsyncSession, user_data: CreateCuratorRequest):
    hashed_password = pwd_context.hash(user_data.password)
    user_data.password = hashed_password
    user = Curator(**user_data.dict())
    session.add(user)
    await session.commit()
    return user


async def login_user(session: AsyncSession, username: str, password: str):
    musician_query = select(Musician).where(Musician.login == username)
    curator_query = select(Curator).where(Curator.login == username)

    musician = await session.execute(musician_query)
    curator = await session.execute(curator_query)

    musician = musician.scalar_one_or_none()
    curator = curator.scalar_one_or_none()

    if musician and pwd_context.verify(password, musician.password):
        user_id = musician.musician_id
        user_role = UserRoleEnum.musician
    elif curator and pwd_context.verify(password, curator.password):
        user_id = curator.curator_id
        user_role = UserRoleEnum.curator
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": username, "user_role": user_role.value})

    user_session_query = select(UserSession).where(
        (UserSession.musician_id == user_id) if user_role == UserRoleEnum.musician else
        (UserSession.curator_id == user_id) if user_role == UserRoleEnum.curator else None
    ).order_by(desc(UserSession.created_at)).limit(1)

    existing_user_session = await session.execute(user_session_query)
    existing_session = existing_user_session.scalar_one_or_none()

    if existing_session:
        existing_session.session_id = str(uuid4())
        existing_session.access_token = access_token
    else:
        user_session = UserSession(
            musician_id=user_id if user_role == UserRoleEnum.musician else None,
            curator_id=user_id if user_role == UserRoleEnum.curator else None,
            user_role=user_role,
            access_token=access_token
        )
        session.add(user_session)

    await session.commit()

    return user_id, user_role, access_token


# async def logout_user(user_id: int, user_role: UserRoleEnum, session: AsyncSession):
#     if user_role == UserRoleEnum.musician:
#         session_query = select(UserSession).where(
#             UserSession.musician_id == user_id
#         ).order_by(desc(UserSession.created_at)).limit(1)
#     elif user_role == UserRoleEnum.curator:
#         session_query = select(UserSession).where(
#             UserSession.curator_id == user_id
#         ).order_by(desc(UserSession.created_at)).limit(1)
#     else:
#         raise HTTPException(status_code=401, detail="Invalid user role")
#
#     existing_user_session = await session.execute(session_query)
#     existing_session = existing_user_session.scalar_one_or_none()
#
#     if existing_session:
#         existing_session.is_active = False
#         await session.commit()
#     else:
#         raise HTTPException(status_code=404, detail="User session not found")
