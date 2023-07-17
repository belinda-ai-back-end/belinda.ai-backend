<h3>Belinda.ai
</h3>
<hr>
<h2>🎧 Work name: "Belinda.ai"</h2>
<hr>


<div align="center">

![Python](https://img.shields.io/badge/-Python_3.10+-ececec?style=for-the-badge&logo=python&logoColor=2c3e50)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Ruff](https://img.shields.io/badge/Ruff-ef5552?style=for-the-badge&logo=PyTorchLightning)
![Black](https://img.shields.io/badge/Black-000000?style=for-the-badge)
</div>

<p>
Перед запуском следует создать файл .env и вставить креды базы данных, а также, если нужно будет запустить парсеры, следует вставить ключи от Spotify
Парсинг треков занимает очень-очень много времени
Следует добавить в корень проекта файлы curators.json, playlists.json, tracks.json, processed.txt
</p>

## Build
___
```bash
docker-compose up --build -d postgres
```
```bash
docker-compose up --build belinda_app
```

## Build cron
___
```bash
docker build -t cronjob -f cron.Dockerfile .
```

___
```bash
docker run -d cronjob 
```

## Local Start
___
```bash
uvicorn belinda_app.app:app --host 0.0.0.0 --port 8000
```

## Ruff linting
___
- for check
```bash
poetry run ruff check .
```

## Black 
___
- to autoformat code with the accepted code style
```bash
poetry run black .  
```
 