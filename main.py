from fastapi import FastAPI

from app.handlers.auth import router as router_auth
from database.base import init_db

app = FastAPI()


# для работы alembic нужно сначала его установить, poetry add alembic
# инициализировать alembic init migrations --> Создаст папку в корне migrations
# Настраиваем файл migrations/env.py --> импортируем ниши модели --> from app.models import Base, User, Post
# и указываем в target_metadata наш декларативный класс то есть из from sqlalchemy.orm import declarative_base
# который мы создали для наследования в наших моделях, обычно называется Base --> target_metadata = Base.metadata
# в файле alembic.ini в переменную sqlalchemy.url записываем бд используемую в моем случае
# sqlalchemy.url=sqlite:///db.sqlite3
# затем создаем миграцию alembic revision --autogenerate -m '0001_init' --> 0001_init просто название миграции
# после чего прописываем команду для создание таблиц в бд alembic upgrade head


@app.on_event('startup')
async def startup():
    await init_db(echo=False)


app.include_router(router=router_auth)
