from tortoise.models import Model
from tortoise import fields

class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name

class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
    participants = fields.ManyToManyField('models.Team', related_name='events', through='event_team')

    def __str__(self):
        return self.name


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name

class Malwares(Model):
    id = fields.BigIntField(pk=True)
    first_seen_utc = fields.TextField()
    sha256_hash = fields.TextField()
    md5_hash = fields.TextField()
    sha1_hash = fields.TextField()
    reporter = fields.TextField()
    file_name = fields.TextField()
    file_type_guess = fields.TextField()
    mime_type = fields.TextField()
    signature = fields.TextField()
    clamav = fields.TextField()
    vtpercent = fields.TextField()
    imphash = fields.TextField()
    ssdeep = fields.TextField()
    tlsh = fields.TextField()
    last_seen_utc = fields.TextField()
    ip = fields.TextField()
    url = fields.TextField()
    size = fields.IntField()
    resource_name = fields.TextField()
    maintype = fields.TextField()
    subtype = fields.TextField()
    datetime = fields.DatetimeField()

    def __str__(self):
        return self.first_seen_utc

class Resources(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    maintype = fields.TextField()
    subtype = fields.TextField()
    url = fields.TextField()
    api_url = fields.TextField()
    api_key = fields.TextField()
    api_limit = fields.TextField()
    schedule = fields.TextField()
    schedule_period = fields.TextField()
    datetime = fields.DatetimeField()

    def __str__(self):
        return self.name

class Logs(Model):
    id = fields.IntField(pk=True)
    log = fields.TextField()
    ip = fields.TextField()
    user_name = fields.TextField()
    datetime = fields.DatetimeField()

    def __str__(self):
        return self.name