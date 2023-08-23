import json
from datetime import datetime

import psutil as psutil
from fastapi import Request, APIRouter, HTTPException, UploadFile, File, Depends, Response, status
from sqlalchemy import func, select, exists
from starlette.responses import JSONResponse

from belinda_app.settings import get_settings
from belinda_app.services import (update_deal_status, RoleEnum, authenticate_user,
                                  create_access_token, get_current_user)
from belinda_app.services.auth_service import pwd_context   # позже исправить
from belinda_app.models import (Playlist, Feedback, Curator, Deal, StatusKeyEnumForMusician,
                                StatusKeyEnumForCurator, RatingEnum, Musician, MusicianTrack)
from belinda_app.schemas import (HealthcheckResponse, CreateDealRequest, CreateMusicianRequest,
                                 CreateCuratorRequest, CreateMusicianTrackRequest)
from belinda_app.db.database import SessionLocal, check_database_health, get_session

settings = get_settings()

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Проверка статуса базы
@router.get("/healthcheck", response_model=HealthcheckResponse)
async def healthcheck(request: Request):
    database_status = await check_database_health()
    uptime = (
        datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    ).total_seconds()
    response_status = "OK" if database_status else "Failed"

    return {
        "uptime": uptime,
        "status": response_status,
    }


# Получение 100 рандомных плейлистов
@router.get("/playlists")
async def get_playlists():
    async with SessionLocal() as session:
        query = await session.execute(
            select(Playlist).order_by(func.random()).limit(100)
        )
        random_playlists = query.scalars().all()

    return random_playlists


@router.post("/feedback")
async def set_feedback(musician_id: str, playlist_id: str, rating: RatingEnum):
    async with SessionLocal() as session:
        stmt_user = await session.execute(select(Musician).where(Musician.musician_id == musician_id))
        user = stmt_user.scalar_one_or_none()

        stmt_playlist = await session.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = stmt_playlist.scalar_one_or_none()

        if user is not None and playlist is not None:
            feedback_result = await session.execute(
                select(Feedback).where(
                    Feedback.musician_id == musician_id, Feedback.playlist_id == playlist_id
                )
            )
            feedback = feedback_result.scalar_one_or_none()

            if feedback is not None:
                if feedback.rating == RatingEnum.like and rating == RatingEnum.unlike:
                    message = "Delete like"
                elif (
                    feedback.rating == RatingEnum.dislike
                    and rating == RatingEnum.unlike
                ):
                    message = "Delete dislike"
                else:
                    message = f"Set {rating.capitalize()}"
                feedback.rating = rating
            else:
                feedback = Feedback(
                    musician_id=musician_id, playlist_id=playlist_id, rating=rating
                )
                message = f"Set {rating.capitalize()}"
                session.add(feedback)

            await session.commit()
            return {"message": message}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User or playlist not found"
        )


# Добавление кураторов в базу
@router.post("/upload_curators")
async def upload_curators(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        curator_data = json.loads(contents)

        async with SessionLocal() as session:
            try:
                for curator_name, curator_details in curator_data.items():
                    curator_exists = await session.execute(select(exists().where(
                        Curator.name == curator_name)))
                    if not curator_exists.scalar():
                        curator = Curator(
                            name=curator_details["name"],
                            desc=curator_details["desc"],
                            facebook_link=curator_details["facebook_link"],
                            spotify_link=curator_details["spotify_link"],
                            instagram_link=curator_details["instagram_link"],
                            tiktok_link=curator_details["tiktok_link"],
                            twitter_link=curator_details["twitter_link"],
                            youtube_link=curator_details["youtube_link"],
                            apple_music_link=curator_details["apple_music_link"],
                            mixcloud_link=curator_details["mixcloud_link"],
                            twitch_link=curator_details["twitch_link"],
                        )
                        session.add(curator)

                await session.commit()

                return {"message": "Data uploaded successfully"}
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                await session.close()

    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read JSON file")


# Добавление плейлистов в базу
@router.post("/upload_playlists")
async def upload_playlists(file: UploadFile = File(...)):
    contents = await file.read()
    playlist_data = json.loads(contents)

    async with SessionLocal() as session:
        try:
            for playlist_name, playlist_details in playlist_data.items():
                playlist_exists = await session.execute(select(exists().where(
                    Playlist.id == playlist_name)))
                if not playlist_exists.scalar():
                    images = playlist_details.get("images", [])
                    images_url = images[0]["url"] if images else None

                    playlist = Playlist(
                        id=playlist_name,
                        collaborative=playlist_details["collaborative"],
                        description=playlist_details["description"],
                        external_urls_spotify=playlist_details["external_urls"]["spotify"],
                        images=images,
                        images_url=images_url,
                        href=playlist_details["href"],
                        name=playlist_details["name"],
                        owner_id=playlist_details["owner"]["id"],
                        owner_display_name=playlist_details["owner"]["display_name"],
                        owner_href=playlist_details["owner"]["href"],
                        owner_short=playlist_details["owner_short"],
                        primary_color=playlist_details["primary_color"],
                        public=playlist_details["public"],
                        snapshot_id=playlist_details["snapshot_id"],
                        tracks_total=playlist_details["tracks"]["total"],
                        type=playlist_details["type"],
                        uri=playlist_details["uri"],
                    )
                    session.add(playlist)

            await session.commit()

            return {"message": "Data uploaded successfully"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await session.close()


# Добавление музыкантов в базу
@router.post("/create_musician")
async def create_musician(
    musician_request: CreateMusicianRequest,
) -> dict:
    async with SessionLocal() as session:
        try:
            hashed_password = pwd_context.hash(musician_request.password)
            musician_request.password = hashed_password
            musician_db = Musician(**musician_request.dict())
            session.add(musician_db)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await session.close()
        return {"message": "Musician added successfully"}


# Добавление трека музыканта в базу
@router.post("/create_musician_track")
async def create_musician_track(
    musician_track_request: CreateMusicianTrackRequest
) -> dict:
    musician_track_data = MusicianTrack(**musician_track_request.dict())

    async with SessionLocal() as session:
        try:
            session.add(musician_track_data)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return {"message": "Musician track added successfully"}


# Добавление кураторов в базу
@router.post("/create_curator")
async def create_curator(
    curator_request: CreateCuratorRequest,
) -> dict:
    curator_data = Curator(**curator_request.dict())

    async with SessionLocal() as session:
        try:
            session.add(curator_data)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await session.close()
        return {"message": "Curator data uploaded successfully"}


# Создание сделки
@router.post("/create_deal")
async def create_deal(deal_request: CreateDealRequest) -> dict:
    async with SessionLocal() as session:
        try:
            deal = Deal(**deal_request.dict(), status=StatusKeyEnumForMusician.submit)
            session.add(deal)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return {"message": "Deal created successfully"}


@router.post("/token/")
async def login_for_access_token(login: str, password: str, response: Response):
    db = SessionLocal()
    user = await authenticate_user(login, password=password, db=db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.login})

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return response


@router.get("/protected_data/")
async def get_protected_data(current_user: Musician = Depends(get_current_user)):
    return {"message": "This is protected data.", "user": current_user}


# Выдача всех треков для musician
@router.get("/get_tracks_for_musician/{musician_id}")
async def get_tracks_for_musician(musician_id: str):
    async with SessionLocal() as session:
        try:
            musician_result = await session.execute(select(Musician).where(Musician.musician_id == musician_id))
            musician = musician_result.scalar_one_or_none()
            if not musician:
                raise HTTPException(status_code=404, detail="Musician not found")

            tracks_result = await session.execute(select(MusicianTrack).where(MusicianTrack.musician_id == musician_id))
            tracks = tracks_result.scalars().all()

            return tracks
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


# Выдача всех сделок для curator

@router.get("/get_deals_for_curator/{curator_id}")
async def get_deals_for_curator(curator_id: str):
    async with SessionLocal() as session:
        try:
            curator_result = await session.execute(select(Curator).where(Curator.curator_id == curator_id))
            curator = curator_result.scalar_one_or_none()
            if not curator:
                raise HTTPException(status_code=404, detail="Curator not found")

            deals_result = await session.execute(select(Deal).where(Deal.curator_id == curator_id))
            deals = deals_result.scalars().all()

            return deals
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


# Выдача всех сделок musician_track, которые учавствуют в ней

@router.get("/get_deals_for_track/{musician_track_id}")
async def get_deals_for_track(track_id: str):
    async with SessionLocal() as session:
        try:
            musician_track_result = await session.execute(select(MusicianTrack).where(MusicianTrack.track_id == track_id))
            musician_track = musician_track_result.scalar_one_or_none()
            if not musician_track:
                raise HTTPException(status_code=404, detail="MusicianTrack not found")

            deals_result = await session.execute(select(Deal).where(Deal.musician_track_id == track_id))
            deals = deals_result.scalars().all()

            return deals
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@router.put("/update_deal_status/curator/{deal_id}")
async def update_curator_deal_status(
    deal_id: str,
    new_status: StatusKeyEnumForCurator,
    session: SessionLocal = Depends(get_session)
):
    await update_deal_status(session, deal_id, RoleEnum.curator, new_status)
    return {"message": "Deal status updated successfully for curator"}


@router.put("/update_deal_status/musician/{deal_id}")
async def update_musician_deal_status(
    deal_id: str,
    new_status: StatusKeyEnumForMusician,
    session: SessionLocal = Depends(get_session)
):
    await update_deal_status(session, deal_id, RoleEnum.musician, new_status)
    return {"message": "Deal status updated successfully for musician"}
