from pydantic import BaseModel, validator


class HealthcheckResponse(BaseModel):
    status: str = "OK"
    uptime: float

    @validator("uptime")
    def uptime_validator(cls, v):
        return f"{v:0.2f} seconds"
