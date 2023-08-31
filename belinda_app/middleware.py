import base64
import json

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super(JWTBearer, self).__init__(auto_error=auto_error)  # noqa

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials is not None:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            decoded_token = base64.urlsafe_b64decode(
                credentials.credentials.split(".")[1] + "=" * (4 - len(credentials.credentials.split(".")[1]) % 4),
            )
            payload = json.loads(decoded_token)
            request.scope["user"] = payload
            return credentials.credentials
        else:  # noqa
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False

        try:
            decoded_token = base64.urlsafe_b64decode(jwt_token.split(".")[1] + "=" * (4 - len(jwt_token.split(".")[1]) % 4))
            payload = json.loads(decoded_token)
        except:  # noqa
            payload = None
        if payload is not None:
            is_token_valid = True
        return is_token_valid  # noqa
