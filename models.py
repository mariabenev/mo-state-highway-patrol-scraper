from peewee import *


db = SqliteDatabase('crashes.db', pragmas={'foreign_keys': 1})


class Crash(Model):

    class Meta:
        database = db


class Vehicle(Model):

    class Meta:
        database = db


class Injury(Model):

    class Meta:
        database = db


db.connect()
db.create_tables([Crash, Vehicle, Injury])