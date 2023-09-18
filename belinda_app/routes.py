import json
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

import psutil as psutil
from fastapi import Request, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse

from sqlalchemy import func, select, exists
from sqlalchemy.exc import IntegrityError

import pandas as pd

from belinda_app.settings import get_settings
from belinda_app.services import (update_deal_status, RoleEnum, create_access_token, check_cookie,
                                  ArtistAuthorizationService, CuratorAuthorizationService, ArtistTrackService)
from belinda_app.models import (Playlist, Feedback, Curator, Deal, StatusKeyEnumForArtist,
                                StatusKeyEnumForCurator, RatingEnum, Artist,
                                ArtistTrack, CuratorPlaylist, CuratorSocialLink)
from belinda_app.schemas import (HealthcheckResponse, CreateDealRequest, CreateArtistRequest, ArtistEmail,
                                 CreateCuratorRequest, CuratorEmail, CreateArtistTrackRequest, CuratorPlaylistSchemas)
from belinda_app.db.database import SessionLocal, check_database_health, get_session
from belinda_app.utils import get_user_id
from belinda_app.catboost_predict import pipeline_preprocess, evaluate

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


# Получение 100 плейлистов прогнозируемых моделью
@router.get("/playlists")
async def get_playlists(artist_id: UUID = Depends(get_user_id)):
    async with SessionLocal() as session:
        query = await session.execute(
            select(Playlist.description,
                   Playlist.name,
                   Playlist.ownerDisplayName)
        )
        data = pd.DataFrame(query.fetchall(),
                            columns=["description",
                                     "playlist_name",
                                     "owner_name"])

        query = await session.execute(select(Artist.artistName).
                                      where(Artist.artist_id == artist_id))
        author_name = query.fetchall()[0]
        author_name = author_name["artistName"]

        query = await session.execute(select(ArtistTrack.albumName).
                                      where(ArtistTrack.artist_id == artist_id))
        album_name = query.fetchall()[0]
        album_name = album_name["albumName"]

        query = await session.execute(select(ArtistTrack.trackName).
                                      where(ArtistTrack.artist_id == artist_id))
        track_name = query.fetchall()[0]
        track_name = track_name["trackName"]

        data = pipeline_preprocess.pipeline_preprocess(data,
                                                       author_name=author_name,
                                                       album_name=album_name,
                                                       track_name=track_name)
        data = evaluate.evaluate(data)
        data["name"] = (await session.execute(select(Playlist.name))).fetchall()
        top_playlist_lst_prom = evaluate.pred_playlist(data, 100)

        top_playlist_lst = []
        for i in top_playlist_lst_prom:
            top_playlist_lst.append(i["name"])

    return top_playlist_lst


# Выдача всех треков для artist
@router.get("/get_tracks_for_artist", dependencies=[Depends(check_cookie)])
async def get_tracks_for_artist(artist_id: UUID = Depends(get_user_id)):
    async with SessionLocal() as session:
        try:
            artist_result = await session.execute(select(Artist).where(Artist.artist_id == artist_id))
            artist = artist_result.scalar_one_or_none()
            if not artist:
                raise HTTPException(status_code=404, detail="Artist not found")

            tracks_result = await session.execute(select(ArtistTrack).where(ArtistTrack.artist_id == artist_id))
            tracks = tracks_result.scalars().all()

            return tracks
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


# Выдача всех сделок для curator
@router.get("/get_deals_for_curator", dependencies=[Depends(check_cookie)])
async def get_deals_for_curator(curator_id: UUID = Depends(get_user_id)):
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


# Выдача всех сделок artist_track, которые учавствуют в ней
@router.get("/get_deals_for_track", dependencies=[Depends(check_cookie)])
async def get_deals_for_track(track_id: UUID):
    async with SessionLocal() as session:
        try:
            artist_track_result = await session.execute(
                select(ArtistTrack).where(ArtistTrack.track_id == track_id))
            artist_track = artist_track_result.scalar_one_or_none()
            if not artist_track:
                raise HTTPException(status_code=404, detail="Artist track not found")

            deals_result = await session.execute(select(Deal).where(Deal.artist_track_id == track_id))
            deals = deals_result.scalars().all()

            return deals
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", dependencies=[Depends(check_cookie)])
async def set_feedback(artist_id: UUID, playlist_id: str, rating: RatingEnum):
    async with SessionLocal() as session:
        stmt_user = await session.execute(select(Artist).where(Artist.artist_id == artist_id))
        user = stmt_user.scalar_one_or_none()

        stmt_playlist = await session.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = stmt_playlist.scalar_one_or_none()

        if user is not None and playlist is not None:
            feedback_result = await session.execute(
                select(Feedback).where(
                    Feedback.artist_id == artist_id, Feedback.playlist_id == playlist_id
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
                    artist_id=artist_id, playlist_id=playlist_id, rating=rating
                )
                message = f"Set {rating.capitalize()}"
                session.add(feedback)

            await session.commit()
            return {"message": message}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User or playlist not found"
        )


# Создание сделки
@router.post("/create_deal", dependencies=[Depends(check_cookie)])
async def create_deal(deal_request: CreateDealRequest) -> dict:
    async with SessionLocal() as session:
        try:
            deal = Deal(**deal_request.dict())
            session.add(deal)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return {"message": "Deal created successfully"}


@router.post("/register_artist")
async def register(request: CreateArtistRequest):
    new_artist = await ArtistAuthorizationService().register_artist(request)

    expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(str(new_artist.artist_id), expires_delta)

    await ArtistAuthorizationService().create_artist_session(new_artist.artist_id, access_token)
    response = JSONResponse(content={
        "message": "Successful register",
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
    )
    return response


@router.post("/login_artist")
async def login(request: ArtistEmail):
    artist = await ArtistAuthorizationService().login_artist(request)

    expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(str(artist.artist_id), expires_delta)

    await ArtistAuthorizationService().create_artist_session(artist.artist_id, access_token)
    response = JSONResponse(content={"message": "Successful login"})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
    )
    return response


# Добавление трека музыканта
@router.post("/add_artist_track", dependencies=[Depends(check_cookie)])
async def create_track(artist_track: CreateArtistTrackRequest, artist_id: UUID = Depends(get_user_id)):
    return await ArtistTrackService(artist_track, artist_id)()


@router.post("/logout", dependencies=[Depends(check_cookie)])
async def logout(artist_id: UUID = Depends(get_user_id)):
    await ArtistAuthorizationService().logout_artist(artist_id)

    response = JSONResponse(content={"message": "Logged out successfully"})

    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=-1,
    )

    return response


@router.post("/register_curator")
async def register(request: CreateCuratorRequest):
    new_curator = await CuratorAuthorizationService().register_curator(request)

    expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(str(new_curator.curator_id), expires_delta)

    await CuratorAuthorizationService().create_curator_session(new_curator.curator_id, access_token)
    response = JSONResponse(content={
        "message": "Successful register",
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
    )
    return response


@router.post("/login_curator")
async def login(request: CuratorEmail):
    curator = await CuratorAuthorizationService().login_curator(request)

    expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(str(curator.curator_id), expires_delta)

    await CuratorAuthorizationService().create_curator_session(curator.curator_id, access_token)
    response = JSONResponse(content={"message": "Successful login"})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
    )
    return response


@router.post("/add_curator_playlist", dependencies=[Depends(check_cookie)])
async def add_playlist(
        playlists: List[CuratorPlaylistSchemas],
        curator_id: UUID = Depends(get_user_id),
):
    async with SessionLocal() as session:
        try:
            for pl in playlists:
                playlist = CuratorPlaylist(
                    link=pl.link,
                    cost=pl.cost,
                    curator_id=curator_id
                )
                session.add(playlist)
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save information. ERROR: {e}",
            )
    return {"message": "Add new playlist"}


@router.post("/logout_curator", dependencies=[Depends(check_cookie)])
async def logout(curator_id: UUID = Depends(get_user_id)):
    await CuratorAuthorizationService().logout_curator(curator_id)

    response = JSONResponse(content={"message": "Logged out successfully"})

    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=-1,
    )

    return response


@router.put("/update_deal_status/curator/{deal_id}", dependencies=[Depends(check_cookie)])
async def update_curator_deal_status(
        deal_id: UUID,
        new_status: StatusKeyEnumForCurator,
        session: SessionLocal = Depends(get_session)
):
    await update_deal_status(session, str(deal_id), RoleEnum.curator, new_status)
    return {"message": "Deal status updated successfully for curator"}


@router.put("/update_deal_status_artist/{deal_id}", dependencies=[Depends(check_cookie)])
async def update_artist_deal_status(
        deal_id: UUID,
        new_status: StatusKeyEnumForArtist,
        session: SessionLocal = Depends(get_session)
):
    await update_deal_status(session, str(deal_id), RoleEnum.artist, new_status)
    return {"message": "Deal status updated successfully for artist"}


# Добавление кураторов в базу (не тыкать)
@router.post("/upload_curators")
async def upload_curators(file: UploadFile = File(...)):
    try:
        async with SessionLocal() as session:
            try:
                contents = await file.read()
                curator_data = json.loads(contents)

                for curator_details in curator_data:
                    curator_exists = await session.execute(select(exists().where(
                        Curator.name == curator_details["name"])))
                    if not curator_exists.scalar():
                        social_links = curator_details["socialLinks"]
                        playlists = curator_details.get("playlists", [])

                        curator = Curator(
                            name=curator_details["name"],
                            desc=curator_details["desc"],
                            email=curator_details["email"],
                            password=curator_details["password"],
                        )

                        # Создаем и добавляем связанные сущности
                        for link in social_links:
                            social_link = CuratorSocialLink(
                                name=link["name"],
                                link=link["link"],
                                curator=curator
                            )
                            session.add(social_link)

                        for playlist in playlists:
                            curator_playlist = CuratorPlaylist(
                                link=playlist["link"],
                                cost=playlist.get("cost", 0),
                                curator=curator
                            )
                            session.add(curator_playlist)

                        session.add(curator)

                await session.commit()

                return {"message": "Data uploaded successfully"}
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail="Curator with the same name already exists")
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e))
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
