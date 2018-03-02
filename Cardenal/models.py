# -*- coding: utf-8 -*-
#
import datetime
from peewee import *


class User(Model):
    username = CharField(unique=True)
    last_name = CharField()
    first_name = CharField()
    last_login = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('username',)


def init_db(db_path):
    tables = [User]
    database = SqliteDatabase(db_path)
    for t in tables:
        t._meta.database = database
    database.connect()
    database.create_tables(tables)
    return database
