import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import time

# Укажите ваши учетные данные для Spotify API из переменных окружения
os.environ["SPOTIPY_CLIENT_ID"] = "d360fee5024140a9a22a6a9d181f869d"
os.environ["SPOTIPY_CLIENT_SECRET"] = "0edb102663b94c6f90fe76f3b455e357"

SPOTIPY_REQUEST_TIMEOUT = 60

# Читаем информацию о кураторах из файла JSON
with open("curators.json", "r") as f:
    curators = json.load(f)

# Создаем объект клиента Spotify
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists_json = {}
playlist_data = []
with open("processed.txt", "r", encoding="utf-8") as f:
    processed_set = {line[:-1] for line in f.readlines()}

# Замеряем время начала выполнения скрипта
start_time = time.time()

# Обрабатываем каждого куратора
for curator_name, curator in tqdm(curators.items(), total=len(curators)):
    if curator['spotify_link'] is None:
        continue
    username = curator['spotify_link'].split('/')[-1]

    try:
        # Получаем плейлисты для данного куратора
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

    # Сохраняем список имени куратора и id плейлистов в файл processed.txt
    with open("processed.txt", "a", encoding="utf-8") as f:
        f.write(curator_name + '\n')

# Сохраняем информацию о плейлистах в файл playlists.json
with open("playlists.json", "w", encoding="utf-8") as f:
    json.dump(playlists_json, f, indent=4)

# Замеряем время окончания выполнения скрипта
end_time = time.time()

# Вычисляем и выводим общее время выполнения
execution_time = end_time - start_time
print(f"Парсинг плейлистов завершен за {execution_time:.2f} секунд.")
