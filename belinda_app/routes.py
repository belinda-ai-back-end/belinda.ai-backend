from datetime import datetime

import psutil as psutil
from fastapi import Request, APIRouter, HTTPException
from sqlalchemy import func, select
from starlette import status

from belinda_app.settings import get_settings
from belinda_app.models.feedback import RatingEnum
from belinda_app.models import Playlist, User, Feedback
from belinda_app.schemas.responses import HealthcheckResponse
from belinda_app.db.database import SessionLocal, check_database_health
# from belinda_app.services import parse_spotify_playlists, parse_spotify_tracks, update_curator_data_in_db


settings = get_settings()

router = APIRouter()


# Проверка статуса базы
@router.get("/healthcheck", response_model=HealthcheckResponse)
async def healthcheck(request: Request):
    database_status = await check_database_health()
    uptime = (
            datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    response_status = "OK" if database_status else "Failed"

    return {
        "uptime": uptime,
        "status": response_status,
    }


# Получение 100 рандомных плейлистов
@router.get("/playlists")
async def get_playlists():
    async with SessionLocal() as session:
        query = await session.execute(
            select(Playlist).order_by(func.random()).limit(100)
        )
        random_playlists = query.scalars().all()

    return random_playlists


@router.post("/feedback")
async def set_feedback(user_id: str, playlist_id: str, rating: RatingEnum):
    async with SessionLocal() as session:
        stmt_user = await session.execute(select(User).where(User.user_id == user_id))
        user = stmt_user.scalar_one_or_none()

        stmt_playlist = await session.execute(
            select(Playlist).where(Playlist.id == playlist_id))
        playlist = stmt_playlist.scalar_one_or_none()

        if user is not None and playlist is not None:
            feedback_result = await session.execute(
                select(Feedback).where(
                    Feedback.user_id == user_id, Feedback.playlist_id == playlist_id)
            )
            feedback = feedback_result.scalar_one_or_none()

            if feedback is not None:
                if feedback.rating == RatingEnum.like and rating == RatingEnum.unlike:
                    message = "Delete like"
                elif feedback.rating == RatingEnum.dislike and rating == RatingEnum.unlike:
                    message = "Delete dislike"
                else:
                    message = f"Set {rating.capitalize()}"
                feedback.rating = rating
            else:
                feedback = Feedback(user_id=user_id, playlist_id=playlist_id, rating=rating)
                message = f"Set {rating.capitalize()}"
                session.add(feedback)

            await session.commit()
            return {"message": message}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or playlist not found")


# Обновление данных таблицы "Curators"
# @router.get("/update_curators")
# async def update_curator_data():
#     await update_curator_data_in_db()
#     return {"message": "Data parse an update database table info"}


# Обновление данных таблицы "Playlists"
# @router.get("/parse_playlists")
# async def update_playlist_data():
#     await parse_spotify_playlists()
#     return {"message": "Data parse an update database table info"}


# Обновление данных таблицы "Tracks"
# @router.get("/parse_tracks")
# async def update_track_data():
#     await parse_spotify_tracks()
#     return {"message": "Data parse an update database table info"}


# Добавление пользователей в базу
# @router.post("/create_user")
# async def create_user(
#     user: User,
# ) -> dict:
#     session = SessionLocal()
#     try:
#         session.add(user)
#         await session.commit()
#     except Exception as e:
#         await session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         await session.close()
#     return {"message": "Data uploaded successfully"}
