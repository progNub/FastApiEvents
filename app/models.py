from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy import or_, select, Table

from sqlalchemy.orm import relationship

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
