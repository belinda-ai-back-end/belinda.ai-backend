import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import time

# os.environ["SPOTIPY_CLIENT_ID"] =
# os.environ["SPOTIPY_CLIENT_SECRET"] =

SPOTIPY_REQUEST_TIMEOUT = 60

with open("curators.json", "r") as f:
    curators = json.load(f)

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists_json = {}
playlist_data = []
with open("processed.txt", "r", encoding="utf-8") as f:
    processed_set = {line[:-1] for line in f.readlines()}

start_time = time.time()

for curator_name, curator in tqdm(curators.items(), total=len(curators)):
    if curator['spotify_link'] is None:
        continue
    username = curator['spotify_link'].split('/')[-1]

    try:
        playlists = sp.user_playlists(username)
        while playlists:
            for playlist in playlists['items']:
                playlist_id = playlist['id']
                playlists_json[playlist_id] = playlist
                playlist_data.append((curator_name, playlist_id))

            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None
    except spotipy.exceptions.SpotifyException as e:
        print(f"Ошибка для куратора '{curator_name}': {e}")

    with open("processed.txt", "a", encoding="utf-8") as f:
        f.write(curator_name + '\n')

with open("playlists.json", "w", encoding="utf-8") as f:
    json.dump(playlists_json, f, indent=4)

end_time = time.time()

execution_time = end_time - start_time
print(f"Парсинг плейлистов завершен за {execution_time:.2f} секунд.")
