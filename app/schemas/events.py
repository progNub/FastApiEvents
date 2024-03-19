from datetime import datetime

from pydantic import BaseModel, Field, fields
from app import models


class EventUsers(BaseModel):
    username: str


class Event(BaseModel):
    title: str = Field(max_length=100)
    description: str
    meeting_time: datetime
    users: list[EventUsers]
