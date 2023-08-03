from typing import Generator
from fastapi import HTTPException, Header
from src.db.session import AsyncSession, async_session, session_manager
from fastapi import HTTPException
from jose import jwt
from src.core.config import settings


async def get_db() -> Generator:
    async with async_session() as session:
        yield session


async def get_db_session() -> AsyncSession:
    async with session_manager.session() as session:
        yield session


def get_user_id(authorization: str = Header(None)):
    if authorization:
        # Split the Authorization header into the scheme and the token
        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization Scheme")
        if not token:
            raise HTTPException(status_code=401, detail="Missing Authorization Token")

        # Decode the JWT token and extract the user_id
        return jwt.get_unverified_claims(token)["sub"]

    else:
        # This is returned if there is no Authorization header and therefore no authentication.
        scheme, _, token = settings.SAMPLE_AUTHORIZATION.partition(" ")
        return jwt.get_unverified_claims(token)["sub"]
