import json
from uuid import UUID

from datetime import datetime, timedelta

import psutil as psutil
from fastapi import Request, APIRouter, HTTPException, Depends, status, Cookie, UploadFile, File
from fastapi.responses import JSONResponse

from sqlalchemy import func, select, exists
from sqlalchemy.exc import IntegrityError

from belinda_app.settings import get_settings
from belinda_app.services import (update_deal_status, RoleEnum, create_access_token, check_cookie,
                                  MusicianAuthorizationService, CuratorAuthorizationService)
from belinda_app.models import (Playlist, Feedback, Curator, Deal, StatusKeyEnumForMusician,
                                StatusKeyEnumForCurator, RatingEnum, Musician, MusicianTrack)
from belinda_app.schemas import (HealthcheckResponse, CreateDealRequest, CreateMusicianRequest, MusicianEmail,
                                 CreateCuratorRequest, CuratorEmail)
from belinda_app.db.database import SessionLocal, check_database_health, get_session

settings = get_settings()

router = APIRouter()


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


# Выдача всех треков для musician
@router.get("/get_tracks_for_musician/{musician_id}")
async def get_tracks_for_musician(musician_id: UUID):
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
async def get_deals_for_curator(curator_id: UUID):
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
async def get_deals_for_track(track_id: UUID):
    async with SessionLocal() as session:
        try:
            musician_track_result = await session.execute(
                select(MusicianTrack).where(MusicianTrack.track_id == track_id))
            musician_track = musician_track_result.scalar_one_or_none()
            if not musician_track:
                raise HTTPException(status_code=404, detail="MusicianTrack not found")

            deals_result = await session.execute(select(Deal).where(Deal.musician_track_id == track_id))
            deals = deals_result.scalars().all()

            return deals
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def set_feedback(musician_id: UUID, playlist_id: UUID, rating: RatingEnum):
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


@router.post("/register/musician")
async def register_musician(request: CreateMusicianRequest):
    async with SessionLocal() as session:
        new_musician = await MusicianAuthorizationService.register_musician(session, request)

        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(str(new_musician.musician_id), expires_delta)

        await MusicianAuthorizationService.create_musician_session(session, new_musician.musician_id, access_token)
        response = JSONResponse(content={
            "message": "Successful register",
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
        )
        return response


@router.post("/login/musician")
async def login_musician(request: MusicianEmail):
    async with SessionLocal() as session:
        musician = await MusicianAuthorizationService.login_musician(session, request)

        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(str(musician.musician_id), expires_delta)

        await MusicianAuthorizationService.create_musician_session(session, musician.musician_id, access_token)
        response = JSONResponse(content={
            "message": "Successful email",
            "musician_id": str(musician.musician_id)
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
        )
        return response


@router.post("/logout/musician")
async def logout_musician(musician_id: UUID, access_token: str = Cookie(None)):
    async with SessionLocal() as session:
        await MusicianAuthorizationService.logout_musician(session, musician_id)

    response = JSONResponse(content={"message": "Logged out successfully"})

    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=-1,
    )

    return response


@router.post("/register/curator")
async def register_curator(request: CreateCuratorRequest):
    async with SessionLocal() as session:
        new_curator = await CuratorAuthorizationService.register_curator(session, request)

        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(str(new_curator.curator_id), expires_delta)

        await CuratorAuthorizationService.create_curator_session(session, new_curator.curator_id, access_token)
        response = JSONResponse(content={
            "message": "Successful register",
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
        )
        return response


@router.post("/login/curator")
async def login_curator(request: CuratorEmail):
    async with SessionLocal() as session:
        curator = await CuratorAuthorizationService.login_curator(session, request)

        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(str(curator.curator_id), expires_delta)

        await CuratorAuthorizationService.create_curator_session(session, curator.curator_id, access_token)
        response = JSONResponse(content={
            "message": "Successful email",
            "musician_id": str(curator.curator_id)
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
        )
        return response


@router.post("/logout/curator")
async def logout_curator(curator_id: UUID, access_token: str = Cookie(None)):
    async with SessionLocal() as session:
        await CuratorAuthorizationService.logout_curator(session, curator_id)

    response = JSONResponse(content={"message": "Logged out successfully"})

    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=-1,
    )

    return response


@router.put("/update_deal_status/curator/{deal_id}")
async def update_curator_deal_status(
        deal_id: UUID,
        new_status: StatusKeyEnumForCurator,
        session: SessionLocal = Depends(get_session)
):
    await update_deal_status(session, str(deal_id), RoleEnum.curator, new_status)
    return {"message": "Deal status updated successfully for curator"}


@router.put("/update_deal_status/musician/{deal_id}")
async def update_musician_deal_status(
        deal_id: UUID,
        new_status: StatusKeyEnumForMusician,
        session: SessionLocal = Depends(get_session)
):
    await update_deal_status(session, str(deal_id), RoleEnum.musician, new_status)
    return {"message": "Deal status updated successfully for musician"}


# Добавление кураторов в базу (не тыкать)
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
                        social_links = []
                        social_links_data = curator_details.get("socialLinks", {})
                        for platform, link in social_links_data.items():
                            social_links.append({"name": platform, "link": link})

                        curator = Curator(
                            name=curator_details["name"],
                            desc=curator_details["desc"],
                            email=curator_details.get("email"),
                            password=curator_details.get("password"),
                            socialLinks=social_links,
                            playlists=None
                        )
                        session.add(curator)

                await session.commit()

                return {"message": "Data uploaded successfully"}
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail="Curator with the same name already exists")
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                await session.close()

    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read JSON file")


# Добавление плейлистов в базу (не тыкать)
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
                        externalUrlsSpotify=playlist_details["external_urls"]["spotify"],
                        images=images,
                        imagesUrl=images_url,
                        href=playlist_details["href"],
                        name=playlist_details["name"],
                        ownerId=playlist_details["owner"]["id"],
                        ownerDisplayName=playlist_details["owner"]["display_name"],
                        ownerHref=playlist_details["owner"]["href"],
                        ownerShort=playlist_details["owner_short"],
                        primaryColor=playlist_details["primary_color"],
                        public=playlist_details["public"],
                        snapshotId=playlist_details["snapshot_id"],
                        tracksTotal=playlist_details["tracks"]["total"],
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
