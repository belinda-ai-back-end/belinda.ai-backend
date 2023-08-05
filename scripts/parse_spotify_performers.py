import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

# os.environ["SPOTIPY_CLIENT_ID"] =
# os.environ["SPOTIPY_CLIENT_SECRET"] =

auth_manager = SpotifyClientCredentials(requests_timeout=20)
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_related_artists(artist_id, popularity_threshold=50, limit=10):
    related_artists = []
    # Получаем список связанных исполнителей
    try:
        related = sp.artist_related_artists(artist_id)

        for artist in related['artists']:
            if artist['popularity'] < popularity_threshold:
                related_artists.append({
                    'id': artist['id'],
                    'name': artist['name']
                })
    except ReadTimeout as e:
        print("Ошибка чтения данных при получении связанных исполнителей: ", e)
        # Повторная попытка получить данные или другие действия
    return related_artists[:limit]


def parse_performers():
    genre = 'indie pop'
    output_file = 'related_artists.json'

    try:
        recommendations = sp.recommendations(seed_genres=[genre], limit=5)
    except ReadTimeout as e:
        print("Ошибка чтения данных при получении рекомендаций: ", e)
        recommendations = {'tracks': []}  # Инициализация пустого списка треков

    result = []

    for track in recommendations['tracks']:
        track_artists = track['artists']

        for artist in track_artists:
            artist_id = artist['id']
            artist_name = artist['name']
            # Получаем связанных исполнителей с учетом порога популярности
            related_artists = get_related_artists(artist_id, popularity_threshold=40, limit=10)

            artist_info = {
                'artist_name': artist_name,
                'related_artists': related_artists
            }

            result.append(artist_info)

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, indent=4, ensure_ascii=False)

    print(f'Информация об исполнителях сохранена в файле: {output_file}')


if __name__ == '__main__':
    parse_performers()
