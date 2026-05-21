from fastapi import APIRouter

from app.auth.cognito import create_dev_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/dev-token")
async def dev_token(sub: str = "tech-demo") -> dict:
    if not settings.auth_dev_mode:
        return {"error": "Dev tokens disabled in production"}
    return {"access_token": create_dev_token(sub), "token_type": "bearer"}
