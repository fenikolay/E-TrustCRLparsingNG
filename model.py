import os
import sqlite3
import shutil
import datetime
from peewee import Model, CharField, SqliteDatabase, DateTimeField, IntegerField, DateField
from configurator import configurator

bd_backup_name = str('cert_crl.db_') + datetime.datetime.now().strftime('%Y%m%d') + '.bkp'
if os.path.isfile(bd_backup_name):
    configurator.logg.info(bd_backup_name + ' exist')
    connect = sqlite3.connect(configurator.config['Bd']['name'])
    db = SqliteDatabase(configurator.config['Bd']['name'])
else:
    shutil.copy2('cert_crl.db', bd_backup_name)
    configurator.logg.info(bd_backup_name + ' created')
    connect = sqlite3.connect(configurator.config['Bd']['name'])
    db = SqliteDatabase(configurator.config['Bd']['name'])

class UC(Model):
    ID = IntegerField(primary_key=True)
    Registration_Number = IntegerField()
    INN = IntegerField()
    OGRN = IntegerField()
    Full_Name = CharField()
    Email = CharField()
    Name = CharField()
    URL = CharField()
    AddresCode = CharField()
    AddresName = CharField()
    AddresIndex = CharField()
    AddresAddres = CharField()
    AddresStreet = CharField()
    AddresTown = CharField()

    class Meta:
        database = db


class CERT(Model):
    ID = IntegerField(primary_key=True)
    Registration_Number = IntegerField()
    Name = CharField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    Data = CharField()

    class Meta:
        database = db


class CRL(Model):
    ID = IntegerField(primary_key=True)
    Registration_Number = IntegerField()
    Name = CharField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()

    class Meta:
        database = db


class WatchingCRL(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField()
    INN = IntegerField()
    OGRN = IntegerField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()
    status = CharField()
    download_status = CharField()
    download_count = CharField()
    last_download = DateTimeField()
    last_update = DateTimeField()
    next_update = DateTimeField()

    class Meta:
        database = db


class WatchingCustomCRL(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField()
    INN = IntegerField()
    OGRN = IntegerField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()
    status = CharField()
    download_status = CharField()
    download_count = CharField()
    last_download = DateTimeField()
    last_update = DateTimeField()
    next_update = DateTimeField()

    class Meta:
        database = db


class WatchingDeletedCRL(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField()
    INN = IntegerField()
    OGRN = IntegerField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()
    status = CharField()
    download_status = CharField()
    download_count = CharField()
    last_download = DateTimeField()
    last_update = DateField()
    next_update = DateField()
    moved_from = CharField()

    class Meta:
        database = db


class Settings(Model):
    ID = IntegerField(primary_key=True)
    name = IntegerField()
    value = CharField()

    class Meta:
        database = db