import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from datetime import timedelta, datetime, timezone
from starlette import status
import jwt
from sqlalchemy import exc

from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "secret_key")
ALGORITHM = "HS512"
USER_IDENTIFIER = "user_id"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

InvalidRefreshTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid refresh token",
    headers={"WWW-Authenticate": "Bearer"},
)

InvalidAccessTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid access token",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_jwt_token_pair(user_id: str) -> tuple[str, str]:
    """ Создает пару токенов.
        :return: access_token, refresh_token
        """
    access_payload = {USER_IDENTIFIER: user_id, 'type': 'access'}
    access_token = _create_token(access_payload, delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    refresh_payload = {USER_IDENTIFIER: user_id, 'type': 'refresh'}
    refresh_token = _create_token(refresh_payload, delta=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS))

    return access_token, refresh_token


def _create_token(payload: dict, delta: timedelta) -> str:
    """ Создает токен.
    :return: token"""
    expires_delta = {'exp': datetime.now(tz=timezone.utc) + delta}
    payload.update(expires_delta)
    return jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)


def get_token_payload(token: str, token_type: str) -> dict:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.exceptions.PyJWTError:
        raise get_invalid_token_exc(token_type)

    if payload.get('type') != token_type:
        raise get_invalid_token_exc(token_type)
    if payload.get(USER_IDENTIFIER) is None:
        raise CredentialsException
    return payload


def get_invalid_token_exc(token_type: str) -> HTTPException:
    if token_type == "access":
        return InvalidAccessTokenException
    else:
        return InvalidRefreshTokenException


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Получение текущего пользователя.
    Parameters:
    - `token` берется из запроса.
    Returns:
    - `User`: Объект пользователя, полученный из базы данных.
    """
    payload = get_token_payload(token, "access")

    try:
        user = await User.get(id=payload[USER_IDENTIFIER])
    except exc.NoResultFound:
        raise CredentialsException

    return user

# token = create_token({'123': '123'}, delta=timedelta(seconds=1))
# print(token)
# time.sleep(1)
# payload = get_token_payload(token)
# time = payload.get('exp')
#
# time2 = datetime.fromtimestamp(time)
# print(time2)
