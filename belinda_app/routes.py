from datetime import datetime
import psutil as psutil
from fastapi import Request, APIRouter

from belinda_app.settings import get_settings
from schemas.responses import HealthcheckResponse

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
