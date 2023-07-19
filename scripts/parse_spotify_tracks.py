import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from tqdm import tqdm
from time import sleep

from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

from spotipy.exceptions import SpotifyException


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


if __name__ == '__main__':
    os.environ["SPOTIPY_CLIENT_ID"] = "ef7c4f9bec4a43d2bf1e51a0251a1cc4"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "97f6f1210e4045219ed699abdceb2f3c"

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    with open("playlists.json", "r", encoding="utf-8") as f:
        playlists = json.load(f)

    with open("processed.txt", "r", encoding="utf-8") as f:
        processed_set = {line[:-1] for line in f.readlines()}

    for playlist_id, _ in tqdm(playlists.items(), total=len(playlists)):

        if playlist_id in processed_set:  # or playlist_id == "3xnJK7IyMx8T95KZtGC1Gs":
            continue

        try:
            tracks = sp.playlist_items(playlist_id)
        except SpotifyException as e:
            print(e.msg)
            continue

        while tracks:
            for i, track in enumerate(tracks['items']):
                track["playlists"] = [playlist_id]
                with open("tracks.json", "a", encoding="utf-8") as f:
                    f.write(json.dumps(track) + "\n")

            if False:  # tracks['next']:
                try:
                    tracks = sp.next(tracks)
                except (ReadTimeoutError, ReadTimeout):
                    print("got ReadTimeoutError or ReadTimeout", flush=True)
            else:
                tracks = None

        with open("processed.txt", "a", encoding="utf-8") as f:
            f.write(playlist_id + '\n')

        sleep(0.2)
