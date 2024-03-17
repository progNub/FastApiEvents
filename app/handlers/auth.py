from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from starlette import status

from app.schemas.auth import UserCreate, User, TokenPair
from app import models
from app.services import auth

router = APIRouter(prefix='/auth')


@router.post('/users', response_model=User)
async def register(user: UserCreate):
    if await models.User.is_username_email_exists(username=user.username, email=user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already exists")
    await models.User.create_user(**user.dict())
    return user


@router.get('/users', response_model=list[User])
async def get_list_users(user: models.User = Depends(auth.get_current_user)):
    if user.is_admin:
        users = await models.User.all()
        return users
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='This action is only available to administrators.')


@router.post('/token', response_model=TokenPair)
async def create_token(user: UserCreate):
    user_model = await models.User.get_valid_user(user.username, user.password)
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')
    access, refresh = auth.create_jwt_token_pair(str(user_model.id))
    return TokenPair(access_token=access, refresh_token=refresh)
