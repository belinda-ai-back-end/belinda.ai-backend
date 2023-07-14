# import json
# import logging
from datetime import datetime

import psutil as psutil
from fastapi import Request, APIRouter, HTTPException  # UploadFile, File
from sqlalchemy import func, select
from starlette import status

from belinda_app.settings import get_settings
from belinda_app.schemas.responses import HealthcheckResponse
from belinda_app.models.feedback import RatingEnum
from belinda_app.models import Playlist, User, Feedback
from belinda_app.db.database import SessionLocal

# from belinda_app.models import Curator, Playlist, User


settings = get_settings()

router = APIRouter()
# logging.basicConfig(level=logging.INFO)


@router.get("/healthcheck", response_model=HealthcheckResponse)
async def healthcheck(request: Request):
    return {
        "uptime": (
            datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        ).total_seconds(),
        "status": "OK",
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
        stmt_user = await session.execute(select(User).where(User.id == user_id))
        user = stmt_user.scalar_one_or_none()

        stmt_playlist = await session.execute(select(Playlist).where(Playlist.id == playlist_id))
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


# Добавление записи о лайке в базу
# @router.post("/like")
# async def put_like():
#     pass
#
#
# # Добавление записи о дизлайке в базу
# @router.post("/dislike")
# async def put_dislike():
#     pass
#
#
# # Добавление записи о снятии лайка/дизлайка в базу
# @router.post("/unlike")
# async def remove_like():
#     pass


# Добавление кураторов в базу
# @router.post("/add_curators/")
# async def create_curators(file: UploadFile = File(...)):
#     try:
#         contents = await file.read()
#         curator_data = json.loads(contents)
#
#         session = SessionLocal()
#         try:
#             for curator_name, curator_details in curator_data.items():
#                 curator = Curator(
#                     name=curator_details["name"],
#                     desc=curator_details["desc"],
#                     facebook_link=curator_details["facebook_link"],
#                     spotify_link=curator_details["spotify_link"],
#                     instagram_link=curator_details["instagram_link"],
#                     tiktok_link=curator_details["tiktok_link"],
#                     twitter_link=curator_details["twitter_link"],
#                     youtube_link=curator_details["youtube_link"],
#                     apple_music_link=curator_details["apple_music_link"],
#                     mixcloud_link=curator_details["mixcloud_link"],
#                     twitch_link=curator_details["twitch_link"],
#                 )
#                 session.add(curator)
#
#             await session.commit()
#
#             return {"message": "Data uploaded successfully"}
#         except Exception as e:
#             await session.rollback()
#             raise HTTPException(status_code=500, detail=str(e))
#         finally:
#             await session.close()
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Failed to read JSON file")


# Добавление плейлистов в базу
# @router.post("/add_playlists/")
# async def create_playlists(file: UploadFile = File(...)):
#     contents = await file.read()
#     playlist_data = json.loads(contents)
#
#     session = SessionLocal()
#     try:
#         for playlist_name, playlist_details in playlist_data.items():
#             playlist = Playlist(
#                 id=playlist_name,
#                 collaborative=playlist_details["collaborative"],
#                 description=playlist_details["description"],
#                 external_urls_spotify=playlist_details["external_urls"]["spotify"],
#                 href=playlist_details["href"],
#                 name=playlist_details["name"],
#                 owner_id=playlist_details["owner"]["id"],
#                 owner_display_name=playlist_details["owner"]["display_name"],
#                 owner_href=playlist_details["owner"]["href"],
#                 owner_short=playlist_details["owner_short"],
#                 primary_color=playlist_details["primary_color"],
#                 public=playlist_details["public"],
#                 snapshot_id=playlist_details["snapshot_id"],
#                 tracks_total=playlist_details["tracks"]["total"],
#                 type=playlist_details["type"],
#                 uri=playlist_details["uri"],
#             )
#             session.add(playlist)
#
#         await session.commit()
#
#         return {"message": "Data uploaded successfully"}
#     except Exception as e:
#         await session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         await session.close()


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
