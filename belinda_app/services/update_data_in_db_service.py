import json
import logging
import os

from sqlalchemy import exists, select

from belinda_app.db.database import SessionLocal
from belinda_app.models import Playlist, Track, Curator


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def update_curator_data_in_db():
    curators_file_path = '/app/curators.json'

    if not os.path.exists(curators_file_path):
        logger.error(f"Curators file '{curators_file_path}' not found")
        return {"message": "Curators file not found"}
    with open(curators_file_path, 'r') as file:
        content = file.read()
        curator_data = json.loads(content)
        logger.info(f"Curators file: {curator_data}")

    async with SessionLocal() as session:
        for curator_name, curator_details in curator_data.items():
            curator_exists = await session.execute(select(exists().where(
                Curator.name == curator_name)))
            logger.info(f"Curator data: {curator_name, curator_details}")
            if not curator_exists.scalar():
                curator = Curator(
                    name=curator_details.get("name"),
                    desc=curator_details.get("desc"),
                    facebook_link=curator_details.get("facebook_link"),
                    spotify_link=curator_details.get("spotify_link"),
                    instagram_link=curator_details.get("instagram_link"),
                    tiktok_link=curator_details.get("tiktok_link"),
                    twitter_link=curator_details.get("twitter_link"),
                    youtube_link=curator_details.get("youtube_link"),
                    apple_music_link=curator_details.get("apple_music_link"),
                    mixcloud_link=curator_details.get("mixcloud_link"),
                    twitch_link=curator_details.get("twitch_link"),
                )
            logger.info(f"Curator data: {curator}")
            session.add(curator)

        await session.commit()
        return {"message": "Data uploaded successfully"}


async def update_playlist_data_in_db(playlists_file):
    with open(playlists_file, 'r') as file:
        content = file.read()
        playlist_data = json.loads(content)
        logger.info(f"Playlists file: {playlist_data}")

    async with SessionLocal() as session:
        for playlist_name, playlist_details in playlist_data.items():
            playlist_exists = await session.execute(select(exists().where(
                Playlist.id == playlist_name)))
            logger.info(f"Playlist data: {playlist_name, playlist_details}")
            if not playlist_exists.scalar():
                playlist = Playlist(
                    id=playlist_name,
                    collaborative=playlist_details["collaborative"],
                    description=playlist_details["description"],
                    external_urls_spotify=playlist_details["external_urls"]["spotify"],
                    href=playlist_details["href"],
                    name=playlist_details["name"],
                    owner_id=playlist_details["owner"]["id"],
                    owner_display_name=playlist_details["owner"]["display_name"],
                    owner_href=playlist_details["owner"]["href"],
                    owner_short=playlist_details.get("owner_short", ""),
                    primary_color=playlist_details["primary_color"],
                    public=playlist_details["public"],
                    snapshot_id=playlist_details["snapshot_id"],
                    tracks_total=playlist_details["tracks"]["total"],
                    type=playlist_details["type"],
                    uri=playlist_details["uri"],
                )
                logger.info(f"Playlist data: {playlist}")
                session.add(playlist)

        await session.commit()
        return {"message": "Data uploaded successfully"}


async def update_track_data_in_db(track_data_file):
    with open(track_data_file, 'r') as file:
        content = file.read()
        logger.info(f"Tracks file: {track_data_file}")
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
        logger.info(f"Track file: {track_data_list}")

        for track_data in track_data_list:
            track_exists = await session.execute(
                select(exists().where(Track.id == track_data["id"])))
            if not track_exists.scalar():
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
                logger.info(f"Track file: {track}")
                session.add(track)

        await session.commit()
