import requests
from base64 import b64encode
import json
from datetime import datetime
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
headers = {'Authorization': keys_second,
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

# response = session.get("http://jsonip.com", proxies=proxy)
# print(response.content)
# ip = response.json()['ip']
# print('Public IP is:', ip)

with open(f'recommendations.json', 'a+') as f:
    f.write("[" + "\n")

for x in range(500):
    response = session.get("https://api.spotify.com/v1/recommendations?limit=100&market=ES&seed_genres=indie", headers={
        'Authorization': f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    },
        # proxies=proxy
    )

    tracks = response.json()['tracks']

    dt = datetime.now()
    ts = datetime.timestamp(dt)

    with open(f'recommendations.json', 'a+') as f:
        f.write(json.dumps(tracks) + ",\n")

    print(response.status_code)
    sleep(1.5)
