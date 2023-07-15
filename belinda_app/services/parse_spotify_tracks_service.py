import json
import logging
import os
import time

import spotipy
import asyncio

from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials

from belinda_app.services.update_data_in_db_service import update_track_data_in_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

playlists_file_path = '/app/playlists.json'
processed_file_path = '/app/processed.txt'
tracks_file_path = '/app/tracks.json'

if not os.path.exists(playlists_file_path):
    logger.error(f"Playlists file '{playlists_file_path}' not found")

if not os.path.exists(processed_file_path):
    logger.error(f"Processed file '{processed_file_path}' not found")

if not os.path.exists(playlists_file_path):
    logger.error(f"Tracks file '{tracks_file_path}' not found")


async def parse_spotify_tracks():
    os.environ["SPOTIPY_CLIENT_ID"] = "YOUR_CLIENT_ID"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "YOUR_CLIENT_SECRET"

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    with open(playlists_file_path, "r") as f:
        playlists = json.load(f)

    processed_set = set()
    with open(processed_file_path, "r") as f:
        for line in f:
            processed_set.add(line.strip())

    timeout_duration = 100

    for playlist_id, _ in tqdm(playlists.items(), total=len(playlists)):

        if playlist_id in processed_set:
            continue

        try:
            start_time = time.time()
            while time.time() - start_time < timeout_duration:
                try:
                    tracks = sp.playlist_items(playlist_id)
                    break
                except spotipy.exceptions.SpotifyException as e:
                    if "Read timed out" in str(e):
                        break
        except Exception as e:
            continue

        while tracks:
            for i, track in enumerate(tracks['items']):
                track["playlists"] = [playlist_id]
                with open(tracks_file_path, "a") as f:
                    f.write(json.dumps(track) + "\n")

            if tracks['next']:
                try:
                    tracks = sp.next(tracks)
                except (spotipy.exceptions.SpotifyException, spotipy.client.SpotifyException) as e:
                    logger.error(f"Error retrieving next set of tracks: {e.msg}")
                    break
            else:
                tracks = None

        with open(processed_file_path, "a") as f:
            f.write(playlist_id + '\n')

        await asyncio.sleep(0.2)

    logger.info("Script execution completed.")
    tracks_file = tracks_file_path

    await update_track_data_in_db(tracks_file)

# if __name__ == '__main__':
#     asyncio.run(parse_spotify_tracks())
