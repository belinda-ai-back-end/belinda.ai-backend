# import json
import logging

from fastapi.logger import logger

# from belinda_app.db.database import SessionLocal
# from belinda_app.models import Track


def setup_logger():
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
    logger.handlers = gunicorn_error_logger.handlers


# Скрипт валидации json
# async def track():
#     with open('tracks.json', 'r') as file:
#         content = file.read()
#     json_objects = content.split('\n')
#     fixed_json_objects = []
#
#     for json_str in json_objects:
#         try:
#             json_obj = json.loads(json_str)
#             fixed_json_objects.append(json_obj)
#         except json.JSONDecodeError:
#             pass
#
#     fixed_result = '['
#
#     for i, json_obj in enumerate(fixed_json_objects):
#         fixed_result += json.dumps(json_obj)
#
#         if i < len(fixed_json_objects) - 1:
#             fixed_result += ','
#
#     fixed_result += ']'
#     track_data_list = json.loads(fixed_result)
#     print(fixed_result)
#     session = SessionLocal()
#     try:
#         for track_data in track_data_list:
#             track = Track(
#                 id=track_data["id"],
#                 duration_ms=track_data["duration_ms"],
#                 name=track_data["name"],
#                 popularity=track_data["popularity"],
#                 preview_url=track_data["preview_url"],
#                 album_id=track_data["album"]["id"],
#                 album_href=track_data["album"]["href"],
#                 album_name=track_data["album"]["name"],
#                 album_total_tracks=track_data["album"]["total_tracks"],
#                 artist_id=track_data["album"]["artists"][0]["id"],
#                 artist_name=track_data["album"]["artists"][0]["name"],
#                 artist_href=track_data["album"]["artists"][0]["href"],
#                 playlist_id=track_data["playlists"][0],
#             )
#             session.add(track)
#
#         await session.commit()
#
#         return {"message": "Data uploaded successfully"}
#     except Exception as e:
#         await session.rollback()
#         return "Error"
#     finally:
#         await session.close()
