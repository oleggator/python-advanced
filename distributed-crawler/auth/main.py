import asyncio

import asyncpg
from aio_pika import connect_robust
from aio_pika.patterns import RPC

from models import Users, Tokens, CrawlerStats
from tokenstorage import TokenStorage


async def main():
    connection = await connect_robust('amqp://guest:guest@broker/')

    db_conn = await asyncpg.connect(user='postgres', password='postgres',
                                 database='postgres', host='postgres')

    await Users.ensure_table(db_conn)
    await Tokens.ensure_table(db_conn)
    await CrawlerStats.ensure_table(db_conn)
    token_storage = TokenStorage(db_conn)

    channel = await connection.channel()
    rpc = await RPC.create(channel)
    await rpc.register('signup', token_storage.signup, auto_delete=True)
    await rpc.register('login', token_storage.login, auto_delete=True)
    await rpc.register('validate', token_storage.validate, auto_delete=True)
    await rpc.register('expire', token_storage.expire, auto_delete=True)

    return connection


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    conn = loop.run_until_complete(main())

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(conn.close())
        loop.shutdown_asyncgens()
