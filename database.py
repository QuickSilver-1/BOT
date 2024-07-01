from gino import Gino
import sqlalchemy as sa
from typing import List
from aiogram import Dispatcher
from config import config_1
from sqlalchemy import Column, String, sql, ForeignKey, Integer

db = Gino()

class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"

class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())

async def on_start(dispatcher: Dispatcher):
    await db.set_bind(config_1.POSTGRES_URL)

class Order(TimedBaseModel):
    __tablename__ = 'order'

    order_id = Column(Integer(), primary_key=True, autoincrement=True)
    tg_id = Column(ForeignKey('person.tg_id'))
    caption = Column(String(100))
    status = Column(String(30))

    query: sql.select

class Person(TimedBaseModel):
    __tablename__ = 'person'

    username = Column(String(100))
    first_name = Column(String(50))
    last_name = Column(String(50))
    tg_id = Column(String(50), primary_key=True)

    query: sql.select

class Intensive(TimedBaseModel):
    __tablename__ = 'intensive'

    order_id = Column(Integer(), primary_key=True, autoincrement=True)
    tg_id = Column(ForeignKey('person.tg_id'))

    query: sql.select

