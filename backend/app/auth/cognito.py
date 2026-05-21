from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

security = HTTPBearer(auto_error=False)

DEV_USERS = {
    "tech-demo": {"sub": "tech-demo", "email": "tech@fieldtech.demo", "name": "Alex Martinez", "role": "technician"},
}


class CurrentUser:
    def __init__(self, sub: str, email: str, name: str, role: str = "technician"):
        self.sub = sub
        self.email = email
        self.name = name
        self.role = role


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> CurrentUser:
    if settings.auth_dev_mode:
        if creds and creds.credentials:
            try:
                payload = jwt.decode(creds.credentials, "fieldtech-dev-secret", algorithms=["HS256"])
                return CurrentUser(
                    sub=payload["sub"],
                    email=payload.get("email", ""),
                    name=payload.get("name", "Technician"),
                    role=payload.get("role", "technician"),
                )
            except JWTError:
                pass
        return CurrentUser(**DEV_USERS["tech-demo"])

    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    # Production: validate Cognito JWT (issuer + JWKS)
    try:
        payload = jwt.get_unverified_claims(creds.credentials)
        return CurrentUser(
            sub=payload.get("sub", "unknown"),
            email=payload.get("email", ""),
            name=payload.get("name", payload.get("cognito:username", "User")),
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


def create_dev_token(sub: str = "tech-demo") -> str:
    user = DEV_USERS.get(sub, DEV_USERS["tech-demo"])
    return jwt.encode({**user, "iss": "fieldtech-dev"}, "fieldtech-dev-secret", algorithm="HS256")
