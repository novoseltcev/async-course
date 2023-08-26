from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient, HTTPError

from app.settings import get_settings

router = APIRouter()


@router.post('/auth')
async def provide_auth(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Any:
    try:
        async with AsyncClient() as client:
            response = await client.post(
                str(get_settings().auth.TOKEN_URL),
                data={
                    'username': form.username,
                    'password': form.password,
                    'client_id': get_settings().auth.ID,
                    'client_secret': get_settings().auth.SECRET,
                },
            )
    except HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.args,
        ) from e

    if response.status_code == 200:
        return cast(dict, response.json())

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
