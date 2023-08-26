from datetime import UTC, datetime
from typing import Annotated, cast
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.db import AsyncSession, get_session
from app.models.entities import Account, AuthorizedService
from app.settings import get_settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter()


async def get_service(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthorizedService:
    client_id, client_secret = form.client_id, form.client_secret

    if client_id is None or client_secret is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail='Клиенту отказано в доступе',
        )

    result = await db_session.execute(
        sa.select(AuthorizedService)
        .where(AuthorizedService.id_ == client_id)
        .where(AuthorizedService.secret == client_secret),
    )
    service = result.scalar()
    if not service:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail='Клиенту отказано в доступе',
        )

    return service


@router.post('/token')
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[AuthorizedService, Depends(get_service)],
) -> dict:
    result = await db_session.execute(
        sa.select(Account).where(Account.username == form.username),
    )
    account = result.scalar()
    if not account or not pwd_context.verify(form.password, account.encrypted_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return {'access_token': create_access_token(account)}


def create_access_token(account: Account) -> str:
    return jwt.encode(
        {
            'sub': str(account.pid),
            'exp': datetime.now(UTC) + get_settings().jwt.LIFETIME,
        },
        get_settings().jwt.SECRET,
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/verify')
async def verify_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, key=get_settings().jwt.SECRET)
    except JWTError as e:
        raise credentials_exception from e

    pid = cast(UUID, payload['sub'])
    exp = datetime.fromtimestamp(int(payload['exp']), tz=UTC)
    if exp < datetime.now(UTC):
        raise credentials_exception

    account = await db_session.execute(sa.select(Account).where(Account.pid == pid))
    if not account:
        raise credentials_exception
