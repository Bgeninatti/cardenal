# -*- coding: utf-8 -*-
#
import datetime
from peewee import (Model, CharField, DateTimeField, SqliteDatabase,
                    ForeignKeyField, CompositeKey)

database = SqliteDatabase(None)


class BaseModel(Model):

    class Meta:
        database = database


class User(BaseModel):
    last_name = CharField()
    first_name = CharField()
    last_login = DateTimeField(default=datetime.datetime.now)


class Generator(BaseModel):
    name = CharField(unique=True)


class Subscriptions(BaseModel):
    user = ForeignKeyField(User)
    generator = ForeignKeyField(Generator)

    class Meta:
        primary_key = CompositeKey('generator', 'user')


def init_db(db_path):
    database.init(db_path)
    database.connect()
    database.create_tables([User, Generator, Subscriptions])
    return database
