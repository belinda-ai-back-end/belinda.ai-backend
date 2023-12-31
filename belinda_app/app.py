import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from belinda_app.routes import router
from belinda_app.db.database import init_db
from belinda_app.settings import get_settings
from belinda_app.utils import setup_logger   # track

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Belinda.ai",
    description="Helping artists discover the best potential partner for expansion of the audience using AI",
    version="1.0.0",
    docs_url="/docs"
)
settings = get_settings()


@app.on_event("startup")
async def on_startup():
    await init_db()
    app.include_router(router)
    setup_logger()
    logger.error(settings)
    # await track()


app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

if __name__ == "__main__":
    asyncio.run(on_startup())
