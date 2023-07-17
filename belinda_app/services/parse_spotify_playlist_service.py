import json
import os

import spotipy
import logging
import asyncio

from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

from belinda_app.services.update_data_in_db_service import update_playlist_data_in_db


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

playlists_file_path = "/app/playlists.json"
processed_file_path = "/app/processed.txt"
if not os.path.exists(playlists_file_path):
    logger.error(f"Playlists file '{playlists_file_path}' not found")

if not os.path.exists(processed_file_path):
    logger.error(f"Processed file '{processed_file_path}' not found")


async def process_curator(curator_name, curator, sp, playlists_json, processed_set):
    if (
        curator_name in processed_set
        or "spotify_link" not in curator
        or curator["spotify_link"] is None
    ):
        return

    username = curator["spotify_link"].split("/")
    username = username[-1] if username[-1] != "" else username[-2]

    try:
        playlists = await sp.user_playlists(username)
    except (spotipy.exceptions.SpotifyException, spotipy.client.SpotifyException) as e:
        logger.error(f"Error retrieving playlists for {curator_name}: {e.msg}")
        return

    while playlists:
        for i, playlist in enumerate(playlists["items"]):
            playlist["owner_short"] = curator_name
            playlists_json[playlist["id"]] = playlist

        if playlists["next"]:
            try:
                playlists = await sp.next(playlists)
            except (ReadTimeoutError, ReadTimeout) as e:
                logger.error(f"Error retrieving next set of playlists: {e.msg}")
                break
        else:
            playlists = None

    with open(playlists_file_path, "r") as f:
        json.dump(playlists_json, f, indent=4)

    with open(processed_file_path, "r") as f:
        f.write(curator_name + "\n")


async def parse_spotify_playlists():
    os.environ["SPOTIPY_CLIENT_ID"] = "YOUR_CLIENT_ID"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "YOUR_CLIENT_SECRET"

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    curators_file_path = "/app/curators.json"

    if not os.path.exists(curators_file_path):
        logger.error(f"Curators file '{curators_file_path}' not found")
        return {"message": "Curators file not found"}
    with open(curators_file_path, "r") as f:
        curators = json.load(f)

    playlists_json = {}

    with open(playlists_file_path, "r") as f:
        playlists_json = json.load(f)

    processed_set = set()

    with open(processed_file_path, "r") as f:
        for line in f:
            processed_set.add(line.strip())

    tasks = []
    for curator_name, curator in tqdm(curators.items(), total=len(curators)):
        tasks.append(
            process_curator(curator_name, curator, sp, playlists_json, processed_set)
        )

    await asyncio.gather(*tasks)

    logger.info("Script execution completed.")
    await update_playlist_data_in_db(playlists_file_path)


# if __name__ == '__main__':
#     asyncio.run(parse_spotify_playlists())
