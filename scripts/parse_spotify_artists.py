import requests
from base64 import b64encode
import json
from time import sleep


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


# keys_first = basic_auth("",
#                         "")
# keys_second = basic_auth("",
#                    "")
# keys_thirty = basic_auth("",
#                      "")

session = requests.session()
headers = {
    'Authorization': keys_second,
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "client_credentials"
}

response = session.post(
    "https://accounts.spotify.com/api/token",
    headers=headers,
    data=data,
)

access_token = response.json()['access_token']
print("Got accessToken:", access_token)

artists_data = []

for x in range(5):  # Reduced the loop count for testing
    response = session.get("https://api.spotify.com/v1/recommendations?limit=100&market=ES&seed_genres=indie", headers={
        'Authorization': f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    })

    tracks = response.json()['tracks']

    for track in tracks:
        artists = track['artists']
        for artist in artists:
            artist_id = artist['id']
            artist_info_response = session.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers={
                'Authorization': f"Bearer {access_token}"
            })
            artist_info = artist_info_response.json()
            artist_popularity = artist_info.get('popularity', 0)
            if artist_popularity < 50:
                artists_data.append(artist_info)

    print(response.status_code)
    sleep(1.5)

with open('artists.json', 'w', encoding='utf-8') as f:
    json.dump(artists_data, f, ensure_ascii=False, indent=4)
