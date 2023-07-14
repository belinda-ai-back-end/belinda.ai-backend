# import json
import logging
from datetime import datetime

import psutil as psutil
from fastapi import Request, APIRouter  # HTTPException, UploadFile, File
from sqlalchemy import func, select

from belinda_app.settings import get_settings
from belinda_app.schemas.responses import HealthcheckResponse
from belinda_app.models import Playlist
from belinda_app.db.database import SessionLocal

# from belinda_app.models import Curator, Playlist, User


settings = get_settings()

router = APIRouter()
logging.basicConfig(level=logging.INFO)


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
