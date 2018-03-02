# -*- coding: utf-8 -*-
#
import datetime
from peewee import *

database = SqliteDatabase(None)


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


def init_db(db_path):
    database.init(db_path)
    database.connect()
    database.create_tables([User])
    return database
