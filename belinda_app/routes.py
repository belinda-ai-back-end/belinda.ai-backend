## import json
from datetime import datetime

import psutil as psutil
from fastapi import Request, APIRouter ###, HTTPException, UploadFile, File

from belinda_app.settings import get_settings
from belinda_app.schemas.responses import HealthcheckResponse
# from belinda_app.db.database import SessionLocal
# from belinda_app.models import Curator

settings = get_settings()

router = APIRouter()


@router.get("/healthcheck", response_model=HealthcheckResponse)
async def healthcheck(request: Request):
    return {
        "uptime": (
            datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        ).total_seconds(),
        "status": "OK",
    }


# @router.post("/curators/")
# async def create_curators(file: UploadFile = File(...)):
#     try:
#         contents = await file.read()
#         curator_data = json.loads(contents)
#
#         session = SessionLocal()
#         try:
#             for curator_name, curator_details in curator_data.items():
#                 curator = Curator(
#                     name=curator_details["name"],
#                     desc=curator_details["desc"],
#                     facebook_link=curator_details["facebook_link"],
#                     spotify_link=curator_details["spotify_link"],
#                     instagram_link=curator_details["instagram_link"],
#                     tiktok_link=curator_details["tiktok_link"],
#                     twitter_link=curator_details["twitter_link"],
#                     youtube_link=curator_details["youtube_link"],
#                     apple_music_link=curator_details["apple_music_link"],
#                     mixcloud_link=curator_details["mixcloud_link"],
#                     twitch_link=curator_details["twitch_link"],
#                 )
#                 session.add(curator)
#
#             await session.commit()
#
#             return {"message": "Data uploaded successfully"}
#         except Exception as e:
#             await session.rollback()
#             raise HTTPException(status_code=500, detail=str(e))
#         finally:
#             await session.close()
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Failed to read JSON file")
