import peewee


db = peewee.SqliteDatabase(
    'crashes.db',
    pragmas={'foreign_keys': 1}
)


class Crash(peewee.Model):
    incident_num = peewee.CharField(primary_key=True)
    investigated_by = peewee.CharField()
    gps_latitude = peewee.FloatField()
    gps_longitude = peewee.FloatField()
    date = peewee.DateField()
    time = peewee.TimeField()
    county = peewee.CharField()
    location = peewee.CharField()
    troop = peewee.CharField()
    misc_info = peewee.CharField()

    class Meta:
        database = db

db.connect()
db.create_tables([Crash])
