import logging
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from tqdm import tqdm
from time import sleep

from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

from spotipy.exceptions import SpotifyException

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

if not os.path.exists(tracks_file_path):
    logger.error(f"Tracks file '{tracks_file_path}' not found")


def form_nice_info(track):
    res = {}
    try:
        res["id"] = track["track"]["id"]
        res["duration_ms"] = track["track"]["duration_ms"]
        res["name"] = track["track"]["name"]
        res["popularity"] = track["track"]["popularity"]
        res["preview_url"] = track["track"]["preview_url"]
        res["album"] = track["track"]["album"]
        del res["album"]["available_markets"]
    except (KeyError, TypeError):
        return None
    return res


async def parse_spotify_tracks():
    os.environ["SPOTIPY_CLIENT_ID"] = "YOUR_CLIENT_ID"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "YOUR_CLIENT_SECRET"

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    with open(playlists_file_path, "r") as f:
        playlists = json.load(f)

    with open(processed_file_path, "r") as f:
        processed_set = {line[:-1] for line in f.readlines()}

    for playlist_id, _ in tqdm(playlists.items(), total=len(playlists)):

        if playlist_id in processed_set:
            continue

        try:
            tracks = sp.playlist_items(playlist_id)
        except SpotifyException as e:
            print(e.msg)
            continue

        while tracks:
            for i, track in enumerate(tracks['items']):
                track["playlists"] = [playlist_id]
                with open(tracks_file_path, "a") as f:
                    f.write(json.dumps(track) + "\n")

            if False:
                try:
                    tracks = sp.next(tracks)
                except (ReadTimeoutError, ReadTimeout):
                    print("got ReadTimeoutError or ReadTimeout", flush=True)
            else:
                tracks = None

        with open(processed_file_path, "a") as f:
            f.write(playlist_id + '\n')

        sleep(0.2)
        track_data_file = tracks_file_path

        await update_track_data_in_db(track_data_file)

# if __name__ == '__main__':
#     asyncio.run(parse_spotify_tracks())
