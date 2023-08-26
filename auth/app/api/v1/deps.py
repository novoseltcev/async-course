from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from httpx import AsyncClient
from jose import jwt

from app.db import AsyncSession, get_session
from app.models.entities import Account
from app.models.enums import Role
from app.settings import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> Account:
    async with AsyncClient() as client:
        response = await client.post(
            str(get_settings().auth.VERIFY_URL),
            headers={'Authorization': f'Bearer {token}'},
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    pid = jwt.get_unverified_claims(token).get('sub')
    result = await db_session.execute(sa.select(Account).where(Account.pid == pid))
    user = result.scalar()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if user.role != Role.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return user
