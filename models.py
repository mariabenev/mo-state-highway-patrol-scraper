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
    misc_info = peewee.TextField()

    class Meta:
        database = db


class Vehicle(peewee.Model):
    incident_num = peewee.ForeignKeyField(
        Crash,
        backref='vehicles',
        column_name='incident_num',
    )
    vehicle_num = peewee.IntegerField()
    description = peewee.CharField()
    damage = peewee.CharField()
    disposition = peewee.CharField()
    driver_name = peewee.CharField()
    driver_gender = peewee.CharField()
    driver_age = peewee.CharField()
    safety_device = peewee.CharField()
    driver_city_state = peewee.CharField()
    driver_insurance = peewee.CharField()
    direction = peewee.CharField()

    class Meta:
        database = db
        primary_key = peewee.CompositeKey(
            'incident_num', 'vehicle_num'
        )


class Injury(peewee.Model):
    incident_num = peewee.ForeignKeyField(
        Crash,
        backref='injuries', 
        column_name='incident_num',
    ) 
    vehicle_num = peewee.IntegerField()
    name = peewee.CharField()
    gender = peewee.CharField()
    age = peewee.CharField()
    injury_type = peewee.CharField()
    safety_device = peewee.CharField()
    city_state = peewee.CharField()
    involvement = peewee.CharField()
    disposition = peewee.CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([Crash, Vehicle, Injury])
