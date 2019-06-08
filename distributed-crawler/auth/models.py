from asyncorm.field import DateTimeField, RealField, TextField, IntegerField, SerialField
from asyncorm.model import Model


class Users(Model):
    id = SerialField(primary_key=True)
    name = TextField(default='default user name')
    email = TextField(default='default user name')
    password = TextField(default='default user name')

    created_date = DateTimeField()
    last_login_date = DateTimeField()

    class Meta:
        table_name = 'Users'


class Tokens(Model):
    id = SerialField(primary_key=True)
    user_id = IntegerField()
    token = TextField(default='default user name')

    expire_date = DateTimeField()

    class Meta:
        table_name = 'Tokens'


class CrawlerStats(Model):
    id = SerialField(primary_key=True)
    author_id = IntegerField()

    https = IntegerField()
    domain = TextField(default='default user name')
    pages_count = IntegerField()
    time = DateTimeField()

    avg_time_per_page = RealField()
    max_time_per_page = RealField()
    min_time_per_page = RealField()

    class Meta:
        table_name = 'CrawlerStats'
