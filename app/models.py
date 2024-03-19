from datetime import datetime, timezone
from typing import Self, Tuple, Any

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, ScalarResult
from sqlalchemy import or_, and_, select, Table
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from sqlalchemy.orm import relationship, selectinload

from database.connector import db_conn
from database.base import Base, Manager
from .services.encryption import make_password, check_password

subscribers_table = Table('subscribers',
                          Base.metadata,
                          Column('user_id', Integer, ForeignKey('users.id')),
                          Column('post_id', Integer, ForeignKey('events.id'))
                          )


class User(Base, Manager):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(300), nullable=False)
    email = Column(String(100), nullable=True)
    created = Column(DateTime(), default=datetime.now)
    is_admin = Column(Boolean(), default=False)

    events = relationship("Event", secondary=subscribers_table, back_populates="users")

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<{self.__class__}: {self.username}>"

    @classmethod
    async def create_user(cls, **kwargs):
        password = kwargs.pop("password")
        if password is None:
            raise AttributeError(f"kwargs has no attribute 'password'")
        # Превращаем строку в байты
        password = password.encode()
        kwargs["password"] = make_password(password)
        return await super().create(**kwargs)

    @classmethod
    async def is_username_email_exists(cls, username: str, email: str) -> bool:
        async with db_conn.session as session:
            query = select(cls).where(or_(cls.username == username, cls.email == email))
            result = await session.execute(query)
            if result.scalar_one_or_none() is None:
                return False
            return True

    @classmethod
    async def get_valid_user(cls, username: str, password: str) -> "User":
        user = await User.get(username=username)
        if user:
            if check_password(password, user.password):
                return user


class Event(Base, Manager):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    description = Column(Text())
    meeting_time = Column(DateTime())

    users = relationship("User", secondary=subscribers_table, back_populates="events")

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<{self.__class__}: {self.title}>"

    @classmethod
    async def _get_events_with_session(cls) -> tuple[Select, AsyncSession]:
        """Возвращает подготовленный запрос и текущую сессию"""
        session = db_conn.session
        time_now = datetime.now(timezone.utc)
        query = select(Event)
        query_future_events = query.filter(Event.meeting_time > time_now)
        query_with_users = query_future_events.options(selectinload(Event.users))
        return query_with_users, session

    @classmethod
    async def get_events_with_users(cls) -> ScalarResult[Any]:
        query, session = await cls._get_events_with_session()
        async with session:
            events = await session.execute(query)
            return events.scalars()

    @classmethod
    async def get_users_events(cls, user_id) -> ScalarResult[Any]:
        query, session = await cls._get_events_with_session()
        async with session:
            events = await session.execute(query.filter(Event.users.any(id=user_id)))
            return events.scalars()

    @classmethod
    async def add_user_or_remove(cls, event_id, user_id):
        query, session = await cls._get_events_with_session()
        with session:
            event = await session.execute(query.where(Event.id == event_id))
            user = await session.execute(select(User).where(User.id == user_id))
            event = event.scalar_one_or_none()
            user = user.scalar_one_or_none()

            if event is None:
                raise NoResultFound(f'Event with id {event_id} does not exist')
            if user is None:
                raise NoResultFound(f'User with id {user_id} does not exist')

            if user in event.users:
                event.users.remove(user)
            else:
                event.users.append(user)

            await session.merge(event)
            await session.commit()
            await session.refresh(event)
            return event
