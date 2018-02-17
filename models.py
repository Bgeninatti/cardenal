# -*- coding: utf-8 -*-
#
import datetime
from peewee import *

DATABASE = '/var/www/cardenal/cardenal.db'

database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(unique=True)
    last_name = CharField()
    first_name = CharField()
    last_login = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('username',)


class Notificacion(BaseModel):
    user = ForeignKeyField(User, related_name='notificaciones')
    msg = CharField()
    notified = BooleanField(default=False)
    notified_timestamp = DateTimeField(null=True)


def populate():
    user_zero = User.create(
        id=104741009,
        username='bgeninatti',
        last_name='Geninatti',
        first_name='Bruno'
    )


def create_tables():
    database.connect()
    database.create_tables([User, Notificacion])
    populate()


if __name__ == "__main__":
    create_tables()
