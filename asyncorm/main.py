import asyncio
from datetime import datetime

import asyncpg

from asyncorm.field import IntegerField, TextField, RealField, DateTimeField
from asyncorm.model import Model


class Users(Model):
    id = IntegerField(primary_key=True)
    name = TextField(default='default user name')
    email = TextField(default='default user name')
    password = TextField(default='default user name')

    created_date = DateTimeField()
    last_login_date = DateTimeField()

    class Meta:
        table_name = 'Users'


class Tokens(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    token = TextField(default='default user name')

    expire_date = DateTimeField()

    class Meta:
        table_name = 'Tokens'


class CrawlerStats(Model):
    id = IntegerField(primary_key=True)
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


async def main():
    conn = await asyncpg.connect(user='postgres', password='postgres',
                                 database='postgres', host='127.0.0.1')
    await Users.ensure_table(conn)
    await Tokens.ensure_table(conn)
    await CrawlerStats.ensure_table(conn)

    user = await Users.objects.create(conn,
                                      id=1,
                                      name='user1',
                                      email='kek@kek.com',
                                      password='123',
                                      created_date=datetime.now(),
                                      last_login_date=datetime.now())
    print(user)

    queried_user = await Users.objects.get(conn, pk=1)
    await queried_user.delete(conn)

    queried_user.email = 'peps'
    await queried_user.save(conn)

    queried_user = await Users.objects.get(conn, pk=1)
    print('queried user:', queried_user)


if __name__ == '__main__':
    asyncio.run(main())
