from fastapi import APIRouter, Depends, Path, Body
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound, ArgumentError
from starlette import status
from app import schemas
from app import models
from app.services import auth

router = APIRouter(prefix='/api')


@router.get('/events', response_model=list[schemas.Event])
async def get_list_events():
    events = await models.Event.get_events_with_users()
    return events


@router.post('/event/{event_id}', response_model=schemas.Event)
async def subscribe_or_unsubscribe(event_id: str, action: schemas.SubscribeToEvent,
                                   user: models.User = Depends(auth.get_current_user)):
    try:
        event = await models.Event.add_user_or_remove(event_id=event_id, user=user, action=action.action)
    except NoResultFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc)
    return event


@router.get('/events/my', response_model=list[schemas.Event])
async def get_my_events(user: models.User = Depends(auth.get_current_user)):
    events = await models.Event.get_users_events(user.id)
    return events
