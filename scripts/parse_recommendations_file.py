import time
import json
import requests
from base64 import b64encode


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
headers = {'Authorization': keys_thirty,
           "Content-Type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "client_credentials"
}

# 167.71.241.136:33299
# 64.227.108.25:31908

ip = "64.227.108.25"
port = "31908"

# proxy = {
#     'http': f'socks5://{ip}:{port}',
#     'https': f'socks5://{ip}:{port}'
# }

response = session.post(
    "https://accounts.spotify.com/api/token",
    headers=headers,
    data=data,
    # proxies=proxy
)

access_token = response.json()['access_token']
print("Got accessToken:", access_token)

start_time = time.time()


def fetch_artist_info(artist_id, access_token):
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json',
    }
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    try:
        print(f"Sending request to: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("Request successful")
        artist_info = response.json()
        return artist_info
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error occurred: {json_err}")
        return None


with open('recommendations.json', 'r') as rec_file:
    recommendations_data = json.load(rec_file)

artists_list = []

for recommendation in recommendations_data:
    artist_id = recommendation['artists'][0]['id']
    artist_info = fetch_artist_info(artist_id, access_token)

    if artist_info is not None:
        artist_data = {
            'external_urls': artist_info['external_urls'],
            'followers': artist_info['followers'],
            'genres': artist_info['genres'],
            'href': artist_info['href'],
            'id': artist_info['id'],
            'images': artist_info['images'],
            'name': artist_info['name'],
            'popularity': artist_info['popularity'],
            'type': artist_info['type'],
            'uri': artist_info['uri']
        }
        artists_list.append(artist_data)

with open('artists.json', 'w') as artists_file:
    json.dump(artists_list, artists_file, indent=4)

print("Файл artists.json успешно создан.")

print("Файл artists.json успешно создан.")
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения скрипта: {execution_time} секунд")
