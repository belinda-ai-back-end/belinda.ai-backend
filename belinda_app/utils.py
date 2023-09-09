# import json
import logging

from fastapi.logger import logger
# from fastapi import Request
# from belinda_app.models import Track, Playlist, Curator
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

# async def curator():
#     with open('curators.json', 'r') as file:
#         content = file.read()
#         curator_data = json.loads(content)
#     async with SessionLocal() as session:
#         for curator_name, curator_details in curator_data.items():
#             curator = Curator(
#                 name=curator_details["name"],
#                 desc=curator_details["desc"],
#                 facebookLink=curator_details["facebookLink"],
#                 spotifyLink=curator_details["spotifyLink"],
#                 instagramLink=curator_details["instagramLink"],
#                 tiktokLink=curator_details["tiktokLink"],
#                 twitterLink=curator_details["twitterLink"],
#                 youtubeLink=curator_details["youtubeLink"],
#                 appleMusicLink=curator_details["appleMusicLink"],
#                 mixcloudLink=curator_details["mixcloudLink"],
#                 twitchLink=curator_details["twitchLink"],
#             )
#             session.add(curator)
#
#         await session.commit()
#     return {"message": "Data uploaded successfully"}


# async def playlist():
#     with open('playlists.json', 'r') as file:
#         content = file.read()
#         playlist_data = json.loads(content)
#     async with SessionLocal() as session:
#         for playlist_name, playlist_details in playlist_data.items():
#             images = playlist_details.get("images", [])
#             imagesUrl = images[0]["url"] if images else None
#
#             playlist = Playlist(
#                 id=playlist_name,
#                 collaborative=playlist_details["collaborative"],
#                 description=playlist_details["description"],
#                 externalUrlsSpotify=playlist_details["external_urls"]["spotify"],
#                 images=images,
#                 imagesUrl=imagesUrl,
#                 href=playlist_details["href"],
#                 name=playlist_details["name"],
#                 ownerId=playlist_details["owner"]["id"],
#                 ownerDisplayName=playlist_details["owner"]["display_name"],
#                 ownerHref=playlist_details["owner"]["href"],
#                 ownerShort=playlist_details["ownerShort"],
#                 primaryColor=playlist_details["primaryColor"],
#                 public=playlist_details["public"],
#                 snapshotId=playlist_details["snapshotId"],
#                 tracksTotal=playlist_details["tracks"]["total"],
#                 type=playlist_details["type"],
#                 uri=playlist_details["uri"],
#             )
#             session.add(playlist)
#
#     await session.commit()
#     return {"message": "Data uploaded successfully"}


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
