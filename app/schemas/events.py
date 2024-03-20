from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ValidationInfo

from app import models


class EventUsers(BaseModel):
    username: str


class Event(BaseModel):
    title: str = Field(max_length=100)
    description: str
    meeting_time: datetime
    users: list[EventUsers]


class SubscribeToEvent(BaseModel):
    action: str = Field(..., examples=['add', 'remove'])

    @field_validator('action')
    @classmethod
    def validate_action(cls, act: str):
        allowed_action = ('add', 'remove')
        if act not in allowed_action:
            raise ValueError(f'action must be one of {allowed_action}')
        return act
