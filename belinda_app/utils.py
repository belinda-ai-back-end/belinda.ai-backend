import json
import logging

from fastapi.logger import logger

from belinda_app.models import Curator, Playlist, Track
from belinda_app.db.database import SessionLocal


def setup_logger():
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
    logger.handlers = gunicorn_error_logger.handlers


async def curator():
    with open('curators.json', 'r') as file:
        content = file.read()
        curator_data = json.loads(content)
    async with SessionLocal() as session:
        for curator_name, curator_details in curator_data.items():
            curator = Curator(
                name=curator_details["name"],
                desc=curator_details["desc"],
                facebook_link=curator_details["facebook_link"],
                spotify_link=curator_details["spotify_link"],
                instagram_link=curator_details["instagram_link"],
                tiktok_link=curator_details["tiktok_link"],
                twitter_link=curator_details["twitter_link"],
                youtube_link=curator_details["youtube_link"],
                apple_music_link=curator_details["apple_music_link"],
                mixcloud_link=curator_details["mixcloud_link"],
                twitch_link=curator_details["twitch_link"],
            )
            session.add(curator)

        await session.commit()
    return {"message": "Data uploaded successfully"}


async def playlist():
    with open('playlists.json', 'r') as file:
        content = file.read()
        playlist_data = json.loads(content)
    async with SessionLocal() as session:
        for playlist_name, playlist_details in playlist_data.items():
            images = playlist_details.get("images", [])
            images_url = images[0]["url"] if images else None

            playlist = Playlist(
                id=playlist_name,
                collaborative=playlist_details["collaborative"],
                description=playlist_details["description"],
                external_urls_spotify=playlist_details["external_urls"]["spotify"],
                images=images,
                images_url=images_url,
                href=playlist_details["href"],
                name=playlist_details["name"],
                owner_id=playlist_details["owner"]["id"],
                owner_display_name=playlist_details["owner"]["display_name"],
                owner_href=playlist_details["owner"]["href"],
                owner_short=playlist_details["owner_short"],
                primary_color=playlist_details["primary_color"],
                public=playlist_details["public"],
                snapshot_id=playlist_details["snapshot_id"],
                tracks_total=playlist_details["tracks"]["total"],
                type=playlist_details["type"],
                uri=playlist_details["uri"],
            )
            session.add(playlist)

    await session.commit()
    return {"message": "Data uploaded successfully"}


# # Скрипт валидации json
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
            album_total_tracks = track_data["album"].get(
                "total_tracks")

            artists = track_data["album"].get("artists", [])
            if artists:
                artist_id = artists[0].get("id")
                artist_name = artists[0].get("name")
                artist_href = artists[0].get("href")
            else:
                artist_id = None
                artist_name = None
                artist_href = None

            track = Track(
                id=track_data.get("id"),
                duration_ms=track_data.get("duration_ms"),
                name=track_data.get("name"),
                popularity=track_data.get("popularity"),
                preview_url=track_data.get("preview_url"),
                album_id=track_data["album"].get("id"),
                album_href=track_data["album"].get("href"),
                album_name=track_data["album"].get("name"),
                album_total_tracks=album_total_tracks,
                artist_id=artist_id,
                artist_name=artist_name,
                artist_href=artist_href,
                playlist_id=track_data.get("playlists", [None])[0],
            )
            session.add(track)

        await session.commit()
        return {"message": "Data uploaded successfully"}
