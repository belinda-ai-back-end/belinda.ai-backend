import json
import logging

from fastapi.logger import logger
# from fastapi import Request
# from belinda_app.models import Track
from belinda_app.models import Track
from belinda_app.db.database import SessionLocal


def setup_logger():
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
    logger.handlers = gunicorn_error_logger.handlers


# def get_jwt_token(request: Request):
#     jwt_token = request.headers.get("Authorization", None)
#     if jwt_token is not None:
#         return jwt_token.replace("Bearer ", "")
#     return None


# Скрипт валидации json
async def track():
    with open('tracks.json', 'r') as file:
        content = file.read()
    async with SessionLocal() as session:
        json_objects = content.split('\n')
        fixed_json_objects = []

        for json_str in json_objects:
            try:
                json_obj = json.loads(json_str)
                fixed_json_objects.append(json_obj)
            except json.JSONDecodeError:
                pass

        fixed_result = '['

        for i, json_obj in enumerate(fixed_json_objects):
            fixed_result += json.dumps(json_obj)

            if i < len(fixed_json_objects) - 1:
                fixed_result += ','

        fixed_result += ']'
        track_data_list = json.loads(fixed_result)

        for track_data in track_data_list:
            albumTotalTracks = track_data["album"].get(
                "total_tracks")

            artists = track_data["album"].get("artists", [])
            if artists:
                artistId = artists[0].get("id")
                artistName = artists[0].get("name")
                artistHref = artists[0].get("href")
            else:
                artistId = None
                artistName = None
                artistHref = None

            track = Track(
                id=track_data.get("id"),
                durationMs=track_data.get("duration_ms"),
                name=track_data.get("name"),
                popularity=track_data.get("popularity"),
                previewUrl=track_data.get("preview_url"),
                albumId=track_data["album"].get("id"),
                albumHref=track_data["album"].get("href"),
                albumName=track_data["album"].get("name"),
                albumTotalTracks=albumTotalTracks,
                artistId=artistId,
                artistName=artistName,
                artistHref=artistHref,
                playlist_id=track_data.get("playlists", [None])[0],
            )
            session.add(track)

        await session.commit()
        return {"message": "Data uploaded successfully"}
